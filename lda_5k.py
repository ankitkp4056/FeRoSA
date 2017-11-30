
# coding: utf-8

# In[2]:
print '......logging to lda_log.log  ........'
import logging
logging.basicConfig( filename = 'lda_log.log', format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
import gensim
import numpy as np
import os
import math as m
import pickle
import timeit
import threading

## PARAMETERS:
num_topics= 100
num_workers= 4
num_passes= 2



## JSDiv_0
from scipy.stats import entropy
from numpy.linalg import norm

def JSDiv(P, Q):
    _P = P / norm(P, ord=1)
    _Q = Q / norm(Q, ord=1)
    _M = 0.5 * (_P + _Q)
    ans= 0.5 * (entropy(_P, _M) + entropy(_Q, _M))
    return ans

## To Unicodify a token:
def safe_unicode(obj, *args):
    """ return the unicode representation of obj """
    try:
        return unicode(obj, *args)
    except UnicodeDecodeError:
        # obj is byte string
        ascii_text = str(obj).encode('string_escape')
        return unicode(ascii_text)
    
### Check if dictionary and corpus exist:
dict_name = 'lda_5k/ferosa_dict.dict'
corpus_name = 'lda_5k/ferosa_corpus.mm'

print '\n.....checking if dictionary and corpus files exist.....\n'
if os.path.isfile(dict_name) and os.path.isfile(corpus_name):
    print '\n.....Loading dictionary and corpus files.....\n'
    dictionary = gensim.corpora.Dictionary.load(dict_name)
    corpus = gensim.corpora.MmCorpus(corpus_name)
    if dictionary.num_docs == corpus.num_docs:
        num_docs = dictionary.num_docs

    
else:
    print '\n.....proceeding to generate dictionary and corpus....\n'
    tokenizer = RegexpTokenizer('[a-zA-Z]+')

    # create English stop words list
    en_stop = get_stop_words('en')

    # Create p_stemmer of class PorterStemmer
    p_stemmer = PorterStemmer()
    
    ## Loading paper_array 
    ## paper_array = names of all papers in dataset ordered lexically
    print '.....Loading paper_array from pickled.....'   
    paper_array_path = 'pickled/paper_array.txt'
    papers_to_remove_path = 'pickled/papers_to_remove_5k.txt'

    with open(paper_array_path, "rb") as array_file:
        paper_array = pickle.load(array_file)
    with open(papers_to_remove_path, "rb") as array_file:
        papers_to_remove_5k = pickle.load(array_file)

    for paper in papers_to_remove_5k:
        paper_array.remove(paper)


    ## frac = 1  # fraction of data to consider
    ## print '\n ..... running the code for ' + str(frac) + ' fraction of data!'
    paper_directory = "../2014/papers_text/"
    filenames = [paper_directory + x + ".txt" for x in paper_array]
    doc_list = [open(f).read() for f in filenames]
    #doc_list = [open(f).read() for f in filenames[:int(len(paper_array)*frac)]]
    num_docs=len(doc_list)


    # In[6]:


    # list for tokenized documents in loop
    texts = []

    count=0
    for i in doc_list:
    
        if count%500 == 0:
            print '\n.....preprocessing paper_num: ' +str(count)+'--to--'+str(count+499) 
        count+=1
        # clean and tokenize document string
        raw = i.lower()
        tokens = tokenizer.tokenize(raw)
  
        # Unicodifying
        unicoded_tokens = [safe_unicode(i) for i in tokens ]


        # remove stop words from tokens
        stopped_tokens = [i for i in unicoded_tokens if not i in en_stop]
        # stem tokens
        stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens]         
        # removing words of length < 3 (some integers were interfering in topics otherwise)
        filtered_tokens = [i for i in stemmed_tokens if len(i)>2] 
        # add tokens to list
        texts.append(filtered_tokens)


    # In[7]:

    # turn our tokenized documents into a id <-> term dictionary
    print '.....building dictionary (id<-->word).....'
    dictionary = corpora.Dictionary(texts)
    dictionary.filter_extremes(no_below=100, no_above=0.9)
    print '.....saving dictionary(id<-->word).....'
    dictionary.save('lda_5k/ferosa_dict.dict')
    print '.....dictionary saved.....'

    # In[13]:

    # convert tokenized documents into a document-term matrix
    print '.....building corpus (bag of words format).....'
    corpus = [dictionary.doc2bow(text) for text in texts]
    print '.....corpus_size: ' + str(len(corpus))
    print '.....saving corpus.....'
    corpora.MmCorpus.serialize('lda_5k/ferosa_corpus.mm', corpus)
    print '.....corpus saved.....'




# In[44]:
print '.....check if lda_model exists.....'
lda_model_path = 'lda_5k/lda.model'
if os.path.isfile(lda_model_path):
    ldamodel= models.ldamulticore.LdaMulticore.load(lda_model_path)
    
    
else:
    # generate LDA model
    print '\n .....generating LDA model.....\n'
    print '..... LDA model params:\n'
    print 'num_topics: '+str(num_topics)
    print 'num_workers: '+str(num_workers)
    print 'num_passes: '+str(num_passes)
    ldamodel = models.ldamulticore.LdaMulticore(corpus, num_topics=num_topics, id2word = dictionary, workers=num_workers, passes=num_passes)
    
    # saving LDA model
    print '\n .....saving LDA model.....\n'
    ldamodel.save(lda_model_path)


# In[14]:

print '\n .....printing LDA model.....\n'
for entry in ldamodel.print_topics(num_topics=10, num_words=5):
    print entry


# In[16]:

def get_doc_topics(lda, bow):
    gamma, _ = lda.inference([bow])
    
    topic_dist = gamma[0] / sum(gamma[0])  # normalize distribution
    return topic_dist
    #return [(topicid, topicvalue) for topicid, topicvalue in enumerate(topic_dist)]


# In[17]:
print '\n .....printing topic_dist for 1st paper: \n'
print get_doc_topics(ldamodel, corpus[0])

topic_dist_mat_path = 'lda_5k/jsd/topic_dist_mat.npy'
if os.path.isfile(topic_dist_mat_path):
    print '\n .....loading topic_dist_mat from .....\n' + topic_dist_mat_path
    topic_dist=np.load(topic_dist_mat_path)
else:
    print '\n .....building topic_dist matrix \n'
    topic_dist = []
    for j in xrange(len(corpus)):
        if j%1000==0:
            print '.... on document ' +str(j+1)
        topic_dist.append(get_doc_topics(ldamodel, corpus[j]))
        
    print '\n .....Saving topic_dist_mat to binary at....' + topic_dist_mat_path
    np.save(topic_dist_mat_path,topic_dist)


print '\n .....printing JSD for 1st paper and 1st paper: (must be 0.0) \n'
print m.sqrt(JSDiv(topic_dist[0],topic_dist[0]))
print '\n .....printing JSD for 1st paper and 2nd paper: \n'
print m.sqrt(JSDiv(topic_dist[0],topic_dist[1]))


# In[63]:
print '\n .....Building JSD_mat to replace cosine_mat.....\n'
JSD_mat = np.zeros((num_docs,num_docs))

def build_jsd_mat(topic_dist, JSD_mat, num_start):
    
    start_time = timeit.default_timer()

    for i in range(num_start*100,(num_start+1)*100):    
        if i%50==0:
            elapsed = timeit.default_timer() - start_time
            print '\n\n(thread:'+str(num_start)+ ' ).....elapsed time for last batch '+str(i-49)+'--to--'+str(i)+'='+str(elapsed)
            start_time = timeit.default_timer()

        for j in xrange(num_docs):
            div= JSDiv(topic_dist[i],topic_dist[j])
            if div < 0:
                div=0
            elif div > 1:
                div = 1
            JSD_mat[i][j] = div
    

print '.....starting multiple threads.....'
t = []
for i in xrange(50):
    t.append(threading.Thread(target=build_jsd_mat,args=(topic_dist, JSD_mat,i)))   
for thread in t:
    thread.start()
for thread in t:
    thread.join()


jsd_mat_path = 'lda_5k/jsd/jsd_mat.npy'
if os.path.isfile(jsd_mat_path):
    print '\n .....JSD_mat already exists at .....\n' + jsd_mat_path
    print '\n .....Saving JSD_mat to binary at....' + jsd_mat_path+'_1.npy'
    np.save(jsd_mat_path+'_1.npy',JSD_mat)

else:
    print '\n .....Saving JSD_mat to binary at....' + jsd_mat_path
    np.save(jsd_mat_path,JSD_mat)




