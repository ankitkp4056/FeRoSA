import os
import pickle
import numpy as np
import pandas as pd

print '-----Loading dict_cit_head (dictionary of citation links created from XML files)-----\n '
with open("pickled/dict_cit_head_ml=0.2_multihead_deepdict.txt", "rb") as dict_file:
    outcite_1 = pickle.load(dict_file)

print '-----Loading paper_array-----\n'            
with open('pickled/paper_array.txt', "rb") as array_file:
    paper_array = pickle.load(array_file)  
    
count_outcite_1 = {}
for key in outcite_1.iterkeys():
    count_outcite_1[key] = 0
for key in outcite_1.iterkeys():
    for value in outcite_1[key].itervalues():
        count_outcite_1[key] += len(value)
        

count_incite_1 = {}
for key in outcite_1.iterkeys():
    count_incite_1[key] = 0
for key in outcite_1.iterkeys():
    for value in outcite_1[key].itervalues():
        for entry in value:
            count_incite_1[entry]+=1
                
papers_to_remove =[]
for paper in paper_array:
    if count_incite_1[paper]+count_outcite_1[paper] < 10:
        papers_to_remove.append(paper)
print '----- ' +str(len(papers_to_remove))+' papers have less than 10 links-----\n'

print '-----saving list of liss-linked papers into "papers_to_remove_5k"-----\n'
with open('pickled/papers_to_remove_5k.txt', "wb") as dict_file:
    pickle.dump(papers_to_remove, dict_file) 
    
    
    
print '-----Creating dict_cit_head_5k after removing the less-linked papers-----\n'
   

with open("pickled/dict_cit_head_ml=0.2_multihead_deepdict.txt", "rb") as dict_file:
    outcite_1_5k = pickle.load(dict_file)

for entry in papers_to_remove:
    outcite_1_5k.pop(entry)
for val in outcite_1_5k.values():
    for value in val.values():
        temp = []+value
        for elem in temp:
            if elem in papers_to_remove:
                value.remove(elem)
print '-----Num of entries/papers in new citation network= '+len(list(outcite_1_5k.keys()))+'-----\n'
                
print '----saving dict_cit_head_5k to pickled-----'
with open("pickled/dict_cit_head_5k.txt", "wb") as dict_file:
    pickle.dump(outcite_1_5k ,dict_file)    
                

########-----EXTRA-----########

## ANALYSING CITATION LINKS IN THE NEW CITATION NETWORK         
def analyse_links(dict_cit_count):    
    num_links=0
    count = 0
    c =0
    for val in count_outcite_1_5k.values():
        c+=1
        if val!=0:
            count+=1
        num_links+=val    
    print 'Total_num_of_citation_links= '+str(num_links)
    print 'Total_num_of_non_empty entries= '+str(count)
    print 'Total_num_of_entries= '+str(c)


count_outcite_1_5k = {}
for key in outcite_1_5k.iterkeys():
    count_outcite_1_5k[key] = 0
for key in outcite_1_5k.iterkeys():
    for value in outcite_1_5k[key].itervalues():
        count_outcite_1_5k[key] += len(value)
analyse_links(count_outcite_1_5k)
        
count_incite_1_5k = {}
for key in outcite_1_5k.iterkeys():
    count_incite_1_5k[key] = 0
for key in outcite_1_5k.iterkeys():
    for value in outcite_1_5k[key].itervalues():
        for entry in value:
            count_incite_1_5k[entry]+=1
analyse_links(count_incite_1_5k)








