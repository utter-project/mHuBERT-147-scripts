#!/usr/bin/env/python3
"""Recipe for training a wav2vec-based ctc ASR system with librispeech.
The system employs wav2vec as its encoder. Decoding is performed with
ctc greedy decoder.
To run this recipe, do the following:
> python train_with_wav2vec.py hparams/train_{hf,sb}_wav2vec.yaml
The neural network is trained on CTC likelihood target and character units
are used as basic recognition tokens.

Authors
 * Rudolf A Braun 2022
 * Titouan Parcollet 2022
 * Sung-Lin Yeh 2021
 * Ju-Chieh Chou 2020
 * Mirco Ravanelli 2020
 * Abdel Heba 2020
 * Peter Plantinga 2020
 * Samuele Cornell 2020

>>>>>>>>>>>>>>>  Modified by Marcely Zanon Boito 2023
"""

import os
import sys
import torch
import logging
import speechbrain as sb
from speechbrain.utils.distributed import run_on_main
from hyperpyyaml import load_hyperpyyaml
from pathlib import Path
import jiwer

logger = logging.getLogger(__name__)



# Define training procedure
class ASR(sb.Brain):
    def compute_forward(self, batch, stage):
        """Forward computations from the waveform batches to the output probabilities."""
        batch = batch.to(self.device)
        wavs, wav_lens = batch.sig
        #wavs, wav_lens = wavs.to(self.device), wav_lens.to(self.device)

        # Add augmentation if specified
        if stage == sb.Stage.TRAIN:
            if hasattr(self.modules, "env_corrupt"):
                wavs_noise = self.modules.env_corrupt(wavs, wav_lens)
                wavs = torch.cat([wavs, wavs_noise], dim=0)
                wav_lens = torch.cat([wav_lens, wav_lens])

            if hasattr(self.hparams, "augmentation"):
                wavs = self.hparams.augmentation(wavs, wav_lens)

        # Forward pass

        # Handling SpeechBrain vs HuggingFance pretrained models
        if hasattr(self.modules, "extractor"):  # SpeechBrain pretrained model
            latents = self.modules.extractor(wavs)
            feats = self.modules.encoder_wrapper(latents, wav_lens=wav_lens)[
                "embeddings"
            ]
        else:  # HuggingFace pretrained model
            feats = self.modules.wav2vec2(wavs)

        x = self.modules.enc(feats)
        logits = self.modules.ctc_lin(x)
        p_ctc = self.hparams.log_softmax(logits)

        return p_ctc, wav_lens

    def compute_objectives(self, predictions, batch, stage):
        """Computes the loss (CTC) given predictions and targets."""

        p_ctc, wav_lens = predictions
        #chars, char_lens = batch.char_encoded
        tokens, tokens_lens = batch.tokens

        ids = batch.id

        if hasattr(self.modules, "env_corrupt") and stage == sb.Stage.TRAIN:
            tokens = torch.cat([tokens, tokens], dim=0)
            tokens_lens = torch.cat([tokens_lens, tokens_lens], dim=0)

        loss = self.hparams.ctc_cost(p_ctc, tokens, wav_lens, tokens_lens)
        
        self.ctc_metrics.append(batch.id, p_ctc, tokens, wav_lens, tokens_lens)


        if stage != sb.Stage.TRAIN:

            predicted_tokens = sb.decoders.ctc_greedy_decode(p_ctc, wav_lens, self.hparams.blank_index)
            # Decode token terms to words
            # /!\ ATTENTION, THIS ONLY WORK FOR PHONEME RECOGNITION (NO BOUNDARIES)
            predicted_words = [
                " ".join(self.tokenizer.decode_ndim(utt_seq)).split(" ")
                for utt_seq in predicted_tokens
            ]
            target_words = [wrd.split(" ") for wrd in batch.wrd]
            
            self.cer_metric.append(ids, predicted_words, target_words)

        return loss

    def fit_batch(self, batch):
        outputs = self.compute_forward(batch, sb.Stage.TRAIN)

        loss = self.compute_objectives(outputs, batch, sb.Stage.TRAIN)
        loss.backward()

        if self.check_gradients(loss):
            if not self.hparams.wav2vec2.freeze:
                self.wav2vec_optimizer.step()
            self.model_optimizer.step()

        if not self.hparams.wav2vec2.freeze:
            self.wav2vec_optimizer.zero_grad()
        self.model_optimizer.zero_grad()
        
        return loss.detach()

    def on_stage_start(self, stage, epoch):
        """Gets called at the beginning of each epoch"""
        self.ctc_metrics = self.hparams.ctc_stats()

        if stage != sb.Stage.TRAIN:
            self.cer_metric = self.hparams.cer_computer()

    def on_stage_end(self, stage, stage_loss, epoch):
        """Gets called at the end of an epoch."""
        # Compute/store important stats
        stage_stats = {"loss": stage_loss}
        if stage == sb.Stage.TRAIN:
            self.train_stats = stage_stats
        else:
            stage_stats["CER"] = self.cer_metric.summarize("error_rate")

        # Perform end-of-iteration things, like annealing, logging, etc.
        if stage == sb.Stage.VALID:
            old_lr_model, new_lr_model = self.hparams.lr_annealing_model(
                stage_stats["CER"]
            )
            old_lr_wav2vec, new_lr_wav2vec = self.hparams.lr_annealing_wav2vec(
                stage_stats["CER"]
            ) #here it was stage loss before
            sb.nnet.schedulers.update_learning_rate(
                self.model_optimizer, new_lr_model
            )
            sb.nnet.schedulers.update_learning_rate(
                self.wav2vec_optimizer, new_lr_wav2vec
            )
            self.hparams.train_logger.log_stats(
                stats_meta={
                    "epoch": epoch,
                    "lr_model": old_lr_model,
                    "lr_wav2vec": old_lr_wav2vec,
                },
                train_stats=self.train_stats,
                valid_stats=stage_stats,
            )
            # create checkpoing
            current_epoch = self.hparams.epoch_counter.current
            meta = {"CER": stage_stats["CER"], "epoch": current_epoch}
            name = "checkpoint_epoch" + str(current_epoch)

            self.checkpointer.save_and_keep_only(
                meta=meta, name=name, num_to_keep=10, min_keys=["CER"]
            )

        elif stage == sb.Stage.TEST:
            self.hparams.train_logger.log_stats(
                stats_meta={"Epoch loaded": self.hparams.epoch_counter.current},
                test_stats=stage_stats,
            )
            with open(self.hparams.wer_file, "w") as w:
                w.write("CTC loss stats:\n")
                self.ctc_metrics.write_stats(w)
                w.write("\nCER stats:\n")
                self.cer_metric.write_stats(w)

    def evaluate_batch(self, batch, stage):
        """Computations needed for validation/test batches"""
        predictions = self.compute_forward(batch, stage=stage)
        with torch.no_grad():
            loss = self.compute_objectives(predictions, batch, stage=stage)
        return loss.detach()
    
    def init_optimizers(self):
        "Initializes the wav2vec2 optimizer and model optimizer"
        # Handling SpeechBrain vs HuggingFance pretrained models
        # If the wav2vec encoder is unfrozen, we create the optimizer
        if hasattr(self.modules, "extractor"):  # SpeechBrain pretrained model
            self.wav2vec_optimizer = self.hparams.wav2vec_opt_class(
                self.modules.encoder_wrapper.latent_encoder.parameters()
            )

        else:  # HuggingFace pretrained model
            self.wav2vec_optimizer = self.hparams.wav2vec_opt_class(
                self.modules.wav2vec2.parameters()
            )

        self.model_optimizer = self.hparams.model_opt_class(
            self.hparams.model.parameters()
        )

        if self.checkpointer is not None:
            self.checkpointer.add_recoverable(
                "wav2vec_opt", self.wav2vec_optimizer
            )
            self.checkpointer.add_recoverable("modelopt", self.model_optimizer)


def dataio_prepare(hparams):
    """This function prepares the datasets to be used in the brain class.
    It also defines the data processing pipeline through user-defined functions."""
    
    # Define audio pipeline. In this case, we simply read the path contained
    # in the variable wav with the audio reader.
    @sb.utils.data_pipeline.takes("audio")
    @sb.utils.data_pipeline.provides("sig")
    def audio_pipeline(wav):
        """Load the audio signal. This is done on the CPU in the `collate_fn`."""
        sig = sb.dataio.dataio.read_audio(wav)
        
        return sig

    @sb.utils.data_pipeline.takes("audio")
    @sb.utils.data_pipeline.provides("sig")
    def sp_audio_pipeline(wav):
        """Load the audio signal. This is done on the CPU in the `collate_fn`."""
        sig = sb.dataio.dataio.read_audio(wav)
        sig = sig.unsqueeze(0)
        sig = hparams["speed_perturb"](sig)
        sig = sig.squeeze(0)
        return sig

    #text pipeline
    @sb.utils.data_pipeline.takes("transcription")
    @sb.utils.data_pipeline.provides(
        "wrd", "char_list", "tokens_list", "tokens"
    )
    def text_pipeline(norm_wrds):
        yield norm_wrds
        char_list = norm_wrds.split(" ") #equivalent to list(words) for phonemes (minimum separation possible)
        yield char_list
        tokens_list = label_encoder.encode_sequence(char_list)
        yield tokens_list
        tokens = torch.LongTensor(tokens_list)
        yield tokens

    data_folder = hparams["data_folder"]
    label_encoder = sb.dataio.encoder.CTCTextEncoder()
    datasets = {}

    for dataset in ["train", "valid"]:
        json_path = f"{data_folder}/{dataset}-1.0.json"

        is_use_sp = dataset == "train" and "speed_perturb" in hparams
        audio_pipeline_func = sp_audio_pipeline if is_use_sp else audio_pipeline

        datasets[dataset] = sb.dataio.dataset.DynamicItemDataset.from_json(
            json_path=json_path,
            replacements={"data_root": data_folder},
            dynamic_items=[audio_pipeline_func, text_pipeline],
            output_keys=[
                "id",
                "sig",
                "duration",
                "wrd",
                "char_list",
                "tokens_list",
                "tokens",
                "transcription",
            ],
        )

    for dataset in ["test"]:
        json_path = f"{data_folder}/{dataset}.json"
        datasets[dataset] = sb.dataio.dataset.DynamicItemDataset.from_json(
            json_path=json_path,
            replacements={"data_root": data_folder},
            dynamic_items=[audio_pipeline, text_pipeline],
            output_keys=[
                "id",
                "sig",
                "duration",
                "wrd",
                "char_list",
                "tokens_list",
                "tokens",
                "transcription",
            ],
        )

    lab_enc_file = os.path.join(hparams["save_folder"], "label_encoder.txt")
    special_labels = {
        "blank_label": hparams["blank_index"],
    }
    label_encoder.load_or_create(
        path=lab_enc_file,
        from_didatasets=[datasets["train"]],
        output_key="char_list",
        special_labels=special_labels,
        sequence_input=True,
    )

    # Sorting training data with ascending order makes the code  much
    # faster  because we minimize zero-padding. In most of the cases, this
    # does not harm the performance.
    if hparams["sorting"] == "ascending":
        if hparams["debug"]:
            datasets["train"] = datasets["train"].filtered_sorted(
                key_min_value={"duration": hparams["sorting_min_duration"]},
                key_max_value={"duration": hparams["sorting_max_duration"]},
                sort_key="duration",
                reverse=True,
            )
            datasets["valid"] = datasets["valid"].filtered_sorted(
                key_min_value={"duration": hparams["sorting_min_duration"]},
                key_max_value={"duration": hparams["sorting_max_duration"]},
                sort_key="duration",
                reverse=True,
            )
        else:
            datasets["train"] = datasets["train"].filtered_sorted(
                sort_key="duration"
            )
            datasets["valid"] = datasets["valid"].filtered_sorted(
                sort_key="duration"
            )

        hparams["train_dataloader_opts"]["shuffle"] = False
        hparams["valid_dataloader_opts"]["shuffle"] = False
    elif hparams["sorting"] == "descending":
        # use smaller dataset to debug the model
        if hparams["debug"]:
            datasets["train"] = datasets["train"].filtered_sorted(
                key_min_value={"duration": hparams["sorting_min_duration"]},
                key_max_value={"duration": hparams["sorting_max_duration"]},
                sort_key="duration",
                reverse=True,
            )
            datasets["valid"] = datasets["valid"].filtered_sorted(
                key_min_value={"duration": hparams["sorting_min_duration"]},
                key_max_value={"duration": hparams["sorting_max_duration"]},
                sort_key="duration",
                reverse=True,
            )
        else:
            datasets["train"] = datasets["train"].filtered_sorted(
                sort_key="duration", reverse=True
            )
            datasets["valid"] = datasets["valid"].filtered_sorted(
                sort_key="duration", reverse=True
            )

        hparams["train_dataloader_opts"]["shuffle"] = False
        hparams["valid_dataloader_opts"]["shuffle"] = False
    elif hparams["sorting"] == "random":
        # use smaller dataset to debug the model
        if hparams["debug"]:
            datasets["train"] = datasets["train"].filtered_sorted(
                key_min_value={"duration": hparams["sorting_debug_duration"]},
                key_max_value={"duration": hparams["sorting_max_duration"]},
                sort_key="duration",
            )
            datasets["valid"] = datasets["valid"].filtered_sorted(
                key_min_value={"duration": hparams["sorting_min_duration"]},
                key_max_value={"duration": hparams["sorting_max_duration"]},
                sort_key="duration",
            )

        hparams["train_dataloader_opts"]["shuffle"] = True
        hparams["valid_dataloader_opts"]["shuffle"] = True
    else:
        raise NotImplementedError(
            "sorting must be random, ascending or descending"
        )

    return datasets, label_encoder


if __name__ == "__main__":

    # CLI:
    hparams_file, run_opts, overrides = sb.parse_arguments(sys.argv[1:])

    # If distributed_launch=True then
    # create ddp_group with the right communication protocol
    sb.utils.distributed.ddp_init_group(run_opts)

    with open(hparams_file) as fin:
        hparams = load_hyperpyyaml(fin, overrides)

    # Create experiment directory
    sb.create_experiment_directory(
        experiment_directory=hparams["output_folder"],
        hyperparams_to_save=hparams_file,
        overrides=overrides,
    )

    # here we create the datasets objects as well as tokenization and encoding
    datasets, label_encoder = dataio_prepare(
        hparams
    )
    label_encoder.add_unk()

    # Trainer initialization
    asr_brain = ASR(
        modules=hparams["modules"],
        hparams=hparams,
        run_opts=run_opts,
        checkpointer=hparams["checkpointer"],
    )

    # We load the pretrained wav2vec2 model
    if "pretrainer" in hparams.keys():
        run_on_main(hparams["pretrainer"].collect_files)
        hparams["pretrainer"].load_collected(asr_brain.device)

    # We dynamicaly add the tokenizer to our brain class.
    # NB: This tokenizer corresponds to the one used for the LM!!
    asr_brain.tokenizer = label_encoder


    print(asr_brain.modules)
    # Training
    asr_brain.fit(
        asr_brain.hparams.epoch_counter,
        datasets["train"],
        datasets["valid"],
        train_loader_kwargs=hparams["train_dataloader_opts"],
        valid_loader_kwargs=hparams["valid_dataloader_opts"],
    )

    # Testing
    for dataset in ["valid", "test"]:
        print("evaluating ", dataset)
        asr_brain.evaluate(
            datasets[dataset], test_loader_kwargs=hparams["test_dataloader_opts"], min_key="CER",
        )
