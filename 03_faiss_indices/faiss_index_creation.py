#!/usr/bin/python3
"""
Authors: Marcely Zanon Boito, Nikolaos Lagos

Copyright NAVER LABS Europe 2023

"""

import numpy as np 
import faiss



def load_feature_percent(feat_path, leng_path, percent):
    with open(leng_path, "r") as f:
        lengs = [int(line.rstrip()) for line in f]
        offsets = [0] + np.cumsum(lengs[:-1]).tolist()
    if percent < 0:
        return load_feature(feat_path)
    else:
        print("LOADING ONLY", percent*100, "PERCENT OF THE FEATURES")
        nsample = int(np.ceil(len(lengs) * percent))
        indices = np.random.choice(len(lengs), nsample, replace=False)
        feat = load_feature(feat_path)
        sampled_feat = np.concatenate(
            [feat[offsets[i]: offsets[i] + lengs[i]] for i in indices], axis=0
        )
        print(len(sampled_feat))
        return sampled_feat

def load_feature(feat_path):
    print("LOADING:", feat_path)
    return np.load(feat_path, mmap_mode="r")

def load_lengths(file_path):
    return [int(line.strip()) for line in open(file_path)]

def load_index(index_path):
    index = faiss.read_index(index_path)
    #Make sure we have access to the ivf subindex. We'll need it to get the centroids (clusters)
    index_ivf = faiss.extract_index_ivf(index)
    #This is needed if we need to have access to the original ids 
    #index_ivf.set_direct_map_type(faiss.DirectMap.Hashtable)

    return index,index_ivf

def load_centroids(centroid_path):
    return np.load(centroid_path)

def write_centroids(data, centroid_path, debug=False):
    np.save(centroid_path, data[0])
    if debug:
        #Save the centroids (optionally the original vectors for sanity check) 
        np.save(centroid_path.replace(".npy","_original_vectors.npy"), data[1])

def write_label_file(vecs, label_file):
    with open(label_file, "w") as output_file:
        for audio in vecs:
            str_audio = [str(element) for element in audio]
            output_file.write(" ".join(str_audio) + "\n")

def write_index(index, index_path):
    faiss.write_index(index, index_path)

def write_vectors(vecs, centroid_per_audio_path):
    np.save(centroid_per_audio_path, vecs, allow_pickle=True)

def create_index(f, compression_mode):
    d = f[0].shape[0]
    # Strongest compression that seems to give reasonable results
    index = faiss.index_factory(d, compression_mode)

    #Train the index (kmeans)
    index.train(f)
    #Add the data
    index.add(f)
    index_ivf = faiss.extract_index_ivf(index)
    #Write the index
    return index, index_ivf

def get_centroids_index(xq, index, index_ivf):
    ''' Get centroids '''
    #Get OPQ matix
    opq_mt = faiss.downcast_VectorTransform(index.chain.at(0))
    #Apply pre-transform to query
    xq_t = opq_mt.apply_py(xq)
    #Get centroids C and distances DC on a pre-transformed index
    DC,C = index_ivf.quantizer.search(xq_t, 1)
    return DC, C

def apply_centroids_to_audios(lengths, C):
    vecs = list()
    temp_index = 0
    for i in range(len(lengths)):
        centroid = C[temp_index:temp_index + lengths[i]].ravel()
        vecs.append(centroid)
        temp_index = temp_index + lengths[i]
    return np.array(vecs, dtype=object)

def train_kmeans_independently(f):
    ncentroids = 100 # Number of clusters
    niter = 20
    max_points_per_centroid = 600000000 # Has to be equal to max number of datapoints to avoid sub-sampling
    verbose = True
    d = f[0].shape[0]
    kmeans = faiss.Kmeans(d, ncentroids, niter=niter, verbose=verbose, max_points_per_centroid=max_points_per_centroid)
    kmeans.train(f)
    return kmeans

def get_centroids_kmeans(f, xq):
    kmeans = train_kmeans_independently(f)
    DC, C = kmeans.index.search(xq, 1)
    return DC,C


if __name__ == '__main__':
    print("Not implemented :) \n Please call one of the dataset-specific scripts")





