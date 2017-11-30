
# coding: utf-8
print '\n\n\n-->>> running the code gen_cit_head_threading_deep.py'
# In[1]:

import pandas as pd
import numpy as np
import os
import pickle
import distance
import re
import timeit
import threading

# In[2]:

from lxml import etree
import xml.etree.cElementTree as ET

match_limit = 0.2
print '..... using match_limit = 0.2'
# In[3]:

## Functions to normalize string
def to_normal(a1):
    a1 = re.sub(r'\d+', '', a1)    # removes int
    a1 = re.sub(r'\W+', '', a1)    # removes non-alphanumeric
    #a1 = re.sub(r'[^\w\s]','',a1)  # removes non-alphanumeric(retains whitespaces)
    a1 = re.sub('\n', '', a1)
    a1 = a1.strip()
    a1 = a1.lower()
    return a1

#Function to find match for str(a1) in list_of_strings(a2)
def find_match(a1,a2,ml):
    
    a1 = to_normal(a1)
    dis = 1
    match_elem = None
    
    for elem in a2: 
        #Not applying to_normal to elem in a2(will make code very slow)
        #to_normal must be applied to every element of a2 before passing in the function 
    
        score = distance.nlevenshtein(a1, elem)
        if score<dis:
            match_elem = elem
            dis = score
    if dis<ml:
        return match_elem
    return False


# In[4]:

#Loading 'network.csv' .......
print '.....Loading csv file of network .......'
network = pd.read_csv("network.csv")

#Creating incite and outcite dictionary
print '.....Creating incite and outcite dictionary.....'
incite = {}
outcite = {}
for row in network.iterrows():
    if(type(row[1][1])!=str):
        incite[row[1][0]] = []
    else:
        incite[row[1][0]] = row[1][1].split(',')
    if(type(row[1][2])!=str):
        outcite[row[1][0]] = []
    else:
        outcite[row[1][0]] = row[1][2].split(',')


# In[8]:

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
            paper_array.append(filename[:-4])
    paper_array = sorted(paper_array)
    with open(paper_array_path, "wb") as array_file:
        pickle.dump(paper_array, array_file)

#print '.....Loading the prob_array = list of paper with broken xml..... '
#prob_array_path = 'pickled/prob_array.txt'
#with open(prob_array_path, "rb") as array_file:
#        prob_array = pickle.load(array_file)

#print '.....removing broken xml papers from paper_array......'
#for p in prob_array:
#	paper_array.remove(p)

# In[9]:

## Generate dict from paper_ids.txt 
print '.....Generating dict from paper_ids.txt ..... '
paper_ids=open("../2014/paper_ids.txt","r")
dict_id={}
for line in paper_ids:
    key=line[:8]
    value=to_normal(line[9:-5].strip())
    dict_id[key]=value


# In[10]:

## Initializing outcite_1 aka. dict_cit_head.....
outcite_1 = {}
for paper_id in paper_array:
    outcite_1[paper_id] = {}


# In[11]:

## Generating outcite_1 aka. dict_cit_head.....
print '.....building dict_cit_head .....'

def gen_cit_head(outcite, outcite_1, dict_id, num_start):
    
    start_time = timeit.default_timer()
    loop_count = num_start*500 -1
    for curr_paper in list(outcite_1.keys())[num_start*500:(num_start+1)*500]:
            #print 'paper_id ='+ curr_paper
        loop_count+=1
        doc_name = '../xml/'+curr_paper[:3]+'/'+curr_paper+'-parscit.130908'+'.xml'
        if loop_count%100 ==0:
            elapsed = timeit.default_timer() - start_time
            print '---- (thread: '+str(num_start)+')time taken for last batch '+str(loop_count-99)+'--to--'+str(loop_count)+' = ' +str(elapsed)
            start_time = timeit.default_timer()

        if os.path.isfile(doc_name):
            tree = ET.ElementTree(file= doc_name)
            root = tree.getroot()
        else:
            continue

        heading = []
        body = []
        count = -1
        for elem in root[0][0]:
            count+=1
            if elem.tag == 'sectionHeader' or elem.tag =='subsectionHeader' or elem.tag == 'subsubsectionHeader':
                heading.append([count, elem.text])
            if elem.tag == 'bodyText':
                body.append([count, elem.text])

        cit_head_map = {}
        for elem in tree.iter(tag='citation'):
            citstr = []
            title = []
            body_ind = []
            for child in elem:
                if child.tag == 'title':
                    title = child.text       
                if child.tag == 'contexts':            
                    citstr = child[0].attrib['citStr']
            
            if citstr and title:
                title = to_normal(title)

                for entry in body:
                    if citstr in entry[1]:
                        body_ind.append(entry[0])
     
                if len(body_ind)!=0:
                    
                    cit_head_map[title]=[]
                    for ind in body_ind:
                        #print 'body: '+ str(ind)
                        sect_ind = -1
                        for entry in heading:
                            if entry[0]<ind and entry[0]>sect_ind:
                                sect_ind = entry[0]
        
                        sect = root[0][0][sect_ind].text
                        sect = to_normal(sect)
                        cit_head_map[title].append(sect.strip())
                    
        for entry in outcite[curr_paper]:
            #print entry
            matched = find_match(dict_id[entry],cit_head_map.keys(), match_limit)
            if matched:
                section_list = cit_head_map[matched]
                #print 'section = ' + section
                 #print 'match_found !'
                for section in section_list:
                    
                    if section in list(outcite_1[curr_paper].iterkeys()):
                        outcite_1[curr_paper][section].append(entry)
                    else:
                        outcite_1[curr_paper][section]=[entry]
        
            
        
print '.....starting multiple threads.....'
t = []
for i in xrange(50):
    t.append(threading.Thread(target=gen_cit_head,args=(outcite,outcite_1,dict_id,i)))   
for thread in t:
    thread.start()
for thread in t:
    thread.join()        
    


# In[12]:

# Saving dict_cit_head
print '....saving dict_cit_head in pickled.....'
with open("pickled/dict_cit_head_ml=0.2_multihead_deepdict.txt", "wb") as dict_file:
    pickle.dump(outcite_1, dict_file)
print '.....saved dict_cit_head in pickled.....'


# In[ ]:

### Code Ends Here ###


# In[ ]:




# In[ ]:



