
# coding: utf-8
print '\n\n\n --->>> running  gen_cit_facet_threading_deep_5k_secmap.py .....'
# In[1]:

import pandas as pd
import numpy as np
import os
import pickle
import distance
import re
import ezodf
import timeit
import threading

# In[2]:

match_limit = 0.2
print '..... using match_limit = '+str(match_limit)

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
    paper = None
    
    for elem in a2: 
        #Not applying to_normal to elem in a2(will make code very slow)
        #to_normal must be applied to every element of a2 before passing in the function 
    
        score = distance.nlevenshtein(a1, elem)
        if score<dis:
            paper = elem
            dis = score
    if dis<ml:
        return paper
    return False


# In[4]:

## Loading/Creating paper_array 
## paper_array = names of all papers in dataset ordered lexically
print '.....Loading/Creating paper_array..... '


paper_array_path = 'pickled/paper_array.txt'
papers_to_remove_path = 'pickled/papers_to_remove_5k.txt'
with open(paper_array_path, "rb") as array_file:
    paper_array = pickle.load(array_file)
with open(papers_to_remove_path, "rb") as array_file:
    papers_to_remove_5k = pickle.load(array_file)

for paper in papers_to_remove_5k:
    paper_array.remove(paper)

# In[5]:

# Generating dict from section-mapping-file:
print '.....Generating dict from section-mapping-file....'

doc = ezodf.opendoc('section_mapping.ods')
sheet = doc.sheets[0]
f_dict = {}
for i, row in enumerate(sheet.rows()):
    key=to_normal(str(row[0].value))
    val=str(row[1].value)
    f_dict[key]=val
    
facets = list(set(f_dict.values()))
print facets


# In[6]:

#Loading dict_cit_head
print '.....loading dict_cit_head from pickled..... '
import pickle
with open("pickled/dict_cit_head_5k.txt", "rb") as dict_file:
    outcite_1 = pickle.load(dict_file)


# In[7]:

#Initializing dict_cit_facet (outcite_2 and incite_2)
print '.....Initializing dict_cit_facet (outcite_2 and incite_2).....'




outcite_2 = {}
for paper_id in paper_array:
    outcite_2[paper_id] = {}
    for val in facets:
        outcite_2[paper_id][val]=[] 
        
incite_2 = {}
for paper_id in paper_array:
    incite_2[paper_id] = {}
    for val in facets:
        incite_2[paper_id][val]=[] 
        

section_map_path='pickled/section_map.txt'
print '....checking if section_map exists in pickled.....'
if os.path.isfile(section_map_path):
    print '.....section_map found.... Loading section_map:'
    with open(out_path+'_1', "rb") as dict_file:
        section_map = pickle.load(dict_file)
else:
    print '.....initializing a section_map.....'
    section_map = {}
    # In[8]:

#Generating dict_cit_facet (outcite_2 and incite_2)
print '.....Generating dict_cit_facet (outcite_2 and incite_2)..... '

def gen_faceted_dict(incite_2,outcite_2,outcite_1,f_dict,num_start):
    start_time = timeit.default_timer()
    loop_count = (num_start)*100 -1
    for paper_id in list(outcite_1.keys())[num_start*100:(num_start+1)*100]:
        
        loop_count+=1
        if loop_count%10==0 and num_start%10==0:
            elapsed = timeit.default_timer() - start_time
            print '---- (thread='+str(num_start)+')time taken for last batch '+str(loop_count-9)+'--to--'+str(loop_count)+' = ' +str(elapsed)
            start_time = timeit.default_timer()


        for key in outcite_1[paper_id].keys():
            if outcite_1[paper_id][key] != []:
                #print 'finding match for '+ key
                if key in section_map.keys():
                    matched = section_map[key]
                else:
                    matched = find_match(key,f_dict.keys(), match_limit)
                    section_map[key] = matched
                if matched:
                    #print 'match_found = '+ f_dict[matched]
                    for entry in outcite_1[paper_id][key]:
                        outcite_2[paper_id][f_dict[matched]].append(entry)
                    for entry in outcite_1[paper_id][key]: 
                        incite_2[entry][f_dict[matched]].append(paper_id)
        
            
#        for entry in outcite_1[paper_id]:
#            for heading in entry[1]:
#                matched = find_match(heading,f_dict.keys(), match_limit)
#                if matched:
#                    outcite_2[paper_id][f_dict[matched]].append(entry[0])
#                    incite_2[entry[0]][f_dict[matched]].append(paper_id) 
print '.....starting multiple threads.....'
t = []
for i in xrange(50):
    t.append(threading.Thread(target=gen_faceted_dict,args=(incite_2,outcite_2,outcite_1,f_dict,i)))   
for thread in t:
    thread.start()
for thread in t:
    thread.join()


# In[9]:

# Saving dict_out_cit_facet and dict_in_cit_facet
print '.....saving section_map in pickled.....'
with open(section_map_path, "wb") as dict_file:
    pickle.dump(section_map, dict_file)
print '.....saved section_map in pickled.....'



out_path='pickled/dict_out_cit_facet_ml=0.2_deep_5k.txt'
in_path='pickled/dict_in_cit_facet_ml=0.2_deep_5k.txt'

print '....saving dict_out_cit_facet in pickled.....'
if os.path.isfile(out_path):
    print '..... '+out_path+' already exists. Saving as: '+ out_path+ '_1'
    with open(out_path+'_1', "wb") as dict_file:
        pickle.dump(outcite_2, dict_file)
else:
    with open(out_path, "wb") as dict_file:
        pickle.dump(outcite_2, dict_file)
    print '.....saved dict_out_cit_facet in pickled.....'

print '....saving dict_in_cit_facet in pickled.....'
if os.path.isfile(in_path):
    print '..... '+in_path+' already exists. Saving as: '+ in_path+ '_1'
    with open(in_path+'_1', "wb") as dict_file:
        pickle.dump(incite_2, dict_file)
else:
    with open(in_path, "wb") as dict_file:
        pickle.dump(incite_2, dict_file)
    print '.....saved dict_in_cit_facet in pickled.....'


# In[ ]:

###....code ends here.....###


# In[ ]:




# In[ ]:




# In[ ]:



