
# coding: utf-8

# In[79]:


import os
import pandas as pd
paper_directory = "../text_data/papers_text"

#paper_array = names of all papers in dataset ordered lexically
paper_array = []
for filename in os.listdir(paper_directory):
    if filename.endswith(".txt"): 
        #print(os.path.join(directory, filename))
        paper_array.append(filename[:-4])
paper_array = sorted(paper_array)
print'-----Saving paper_array in pickled-----\n\n'
with open('pickled/paper_array.txt', "wb") as array_file:
        pickle.dump(paper_array,array_file)

incite = {} #dict of all incites of every paper
outcite = {} #dict of all outcites of every paper
for name in paper_array:
    incite[name] = []
    outcite[name] = []

acl_address = "../text_data/acl.txt"
acl = open(acl_address, "r")
lines = acl.readlines()
for data in lines:
    a = data[:8]
    b = data[-9:-1]
    if(b in paper_array and a in paper_array):
        incite[b].append(a)
        outcite[a].append(b)
        
dict_to_write = {}

for (key, value) in incite.items():
    temp = ""
    if (value == []):
        dict_to_write[key] = [temp]
    for x in value:
        temp = temp+","+x
    dict_to_write[key] = [temp[1:]]
for (key, value) in outcite.items():
    temp = ""
    for x in value:
        temp = temp+","+x
    dict_to_write[key].append(temp[1:])

print'-----Saving network.csv in pickled-----\n\n'    
network = pd.DataFrame.from_dict(dict_to_write, orient='index')
network.to_csv("network.csv")

print'-----Saving dict_incite and dict_outcite in pickled-----\n\n'
with open('pickled/dict_incite.txt', "wb") as array_file:
        pickle.dump(incite,array_file)
with open('pickled/dict_outcite.txt', "wb") as array_file:
        pickle.dump(outcite,array_file)




######-----EXTRA-----#####

# Analysing Citation Network

outcit_links=0
for value in outcite.itervalues():
    outcit_links+=len(value)
non_empty = 0
for val in outcite.values():
    if val != []:
        non_empty+=1
print 'non_empty outcite entries= '+str(non_empty)
print 'outcite_links='+str(outcit_links)    


incit_links=0
for value in incite.itervalues():
    incit_links+=len(value)
non_empty = 0
for val in outcite.values():
    if val != []:
        non_empty+=1
print 'non_empty incite entries= '+str(non_empty)
print 'incite_links=' +str(incit_links)    





