
# coding: utf-8

from sklearn.feature_extraction.text import TfidfVectorizer
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


## Loading/Creating paper_array 
## paper_array = names of all papers in dataset ordered lexically
print '.....Loading/Creating paper_array..... '
paper_dir = "../2014/papers_text"
paper_array_path = 'pickled/paper_array.txt'

if os.path.isfile(paper_array_path):
    with open(paper_array_path, "rb") as array_file:
        paper_array = pickle.load(array_file)
else:
    paper_array = []
    for filename in os.listdir(paper_dir):
        if filename.endswith(".txt"): 
            #print(os.path.join(directory, filename))
            paper_array.append(filename[:-4])
    paper_array = sorted(paper_array)
    with open(paper_array_path, "wb") as array_file:
        pickle.dump(paper_array, array_file)
        

## Generating TF-IDF Vectorizer
print '.....Generating TF-IDF Vectorizer....'
filenames = [paper_directory + x + ".txt" for x in paper_array]
documents = [open(f).read() for f in filenames]

raw_matrix = TfidfVectorizer(stop_words = 'english', min_df = 0.01, token_pattern='[a-zA-Z]+')
matrix = raw_matrix.fit_transform(documents)

##Generating cosine-similarity-matrix
print'.....Generating cosine-similarity-matrix.....'
output_matrix = cosine_similarity(matrix)

##saving cosine-similarity-matrix as co_mat.npy in cos
print'.....saving cosine-similarity-matrix as co_mat.npy in cos.....'
np.save("cos/cos_mat.npy", output_matrix)


