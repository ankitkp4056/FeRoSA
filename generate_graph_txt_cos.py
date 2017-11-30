
# coding: utf-8

# In[113]:

import pandas as pd
import numpy as np
import os
import pickle


# In[114]:

# Loading cos-sim-array from cos_mat.npy
print '.....Loading cos-sim-array from cos_mat.npy.....'
cos_sim_array = np.load("cos_5k/cos_mat.npy")

# Min cos_sim value to consider similar
COS_LIMIT = 0.25


# In[115]:

paper_array_path = 'pickled/paper_array.txt'
papers_to_remove_path = 'pickled/papers_to_remove_5k.txt'
with open(paper_array_path, "rb") as array_file:
    paper_array = pickle.load(array_file)
with open(papers_to_remove_path, "rb") as array_file:
    papers_to_remove_5k = pickle.load(array_file)

for paper in papers_to_remove_5k:
    paper_array.remove(paper)


# In[116]:

def cos_sim(p1, p2):
    return cos_sim_array[paper_array.index(p1), paper_array.index(p2)]
 
    


# In[117]:

def cos_sim_top(p1):
    similarity_p1 = cos_sim_array[paper_array.index(p1)]
    top = [paper_array[i] for (i,j) in enumerate(similarity_p1) if j> COS_LIMIT]
    if(len(top)>100):
        print 'nodes_from_cos_sim='+ str(len(top))
        print 'taking only top 50-----\n'
        return top[:50]
    else:
        print 'nodes_from_cos_sim='+ str(len(top))
        return top


# In[118]:

def gen_ind_graph(paper_id, out_net, in_net,facet=None):
    
    nodes = []
    out_1=[]
    in_1=[]
    if facet:
        out_1+=out_net[paper_id][facet]
        in_1+=in_net[paper_id][facet]  
        nodes+=out_1+in_1                                ## adds all 1-hop papers...
           
        for paper in out_1:                              ## adds all 2-hop papers...
            nodes+=out_net[paper][facet]
            nodes+=in_net[paper][facet]
        for paper in in_1:
            nodes+=out_net[paper][facet]
            nodes+=in_net[paper][facet]
        print 'nodes_from_hop='+ str(len(list(set(nodes))))  
    else:
        for value in out_net[paper_id].values():
            out_1+=value
        for value in in_net[paper_id].values():
            in_1+=value
        nodes+=out_1+in_1    
        
        for paper in out_1:                              ## adds all 2-hop papers...
            for value in out_net[paper].values():
                nodes+=value
            for value in in_net[paper].values():
                nodes+=value
            
        for paper in in_1:
            for value in out_net[paper].values():
                nodes+=value
            for value in in_net[paper].values():
                nodes+=value
        print 'nodes_from_hop='+ str(len(list(set(nodes))))  
        
    nodes+=cos_sim_top(paper_id)          ## adds papers above COS_LIMIT

    
    node_set = set(nodes)                            ## takes unique values only...
    nodes = list(node_set)
    
    print 'nodes_from_all='+ str(len(nodes))
    tpm = np.zeros((len(nodes),len(nodes)))
    graph = []
    
    for i in range(1,len(nodes)):
        for j in range(0,i):
            p1 = nodes[i]
            p2 = nodes[j]
            if facet:
                if (p1 in out_net[p2][facet]) or (p2 in out_net[p1][facet]) or (cos_sim(p1,p2)>COS_LIMIT):
                    tpm[i][j] = cos_sim(p1,p2)
                    tpm[j][i] = tpm[i][j]
                    if tpm[i][j]<0 or tpm[i][j]>1:
                        print 'got a problem with '+str(i)+' and '+str(j)
            else:
                out_p2=[]
                out_p1=[]
                for value in out_net[p2].values():
                    out_p2+=value
                for value in out_net[p1].values():
                    out_p1+=value
                    
                if (p1 in out_p2) or (p2 in out_p1) or (cos_sim(p1,p2)>COS_LIMIT):
                    tpm[i][j] = cos_sim(p1,p2)
                    tpm[j][i] = tpm[i][j]
                    if tpm[i][j]<0 or tpm[i][j]>1:
                        print 'got a problem with '+str(i)+' and '+str(j)

                
    for i in xrange(len(nodes)):
        if float(np.sum(tpm[i])) == 0:
            tpm[i]+= (1-np.sum(tpm[i]))/len(nodes)
        else:    
            tpm[i] = tpm[i]/float(np.sum(tpm[i]))*0.9 
            tpm[i]+= (1-np.sum(tpm[i]))/len(nodes)
        
    for i in range(0,len(nodes)):
        for j in range(0,len(nodes)):    
            graph.append([nodes[i], nodes[j], tpm[i,j]])
                
    return graph


# In[119]:

## Function for storing graph as 'paper_id_graph.txt' :

def get_graph_txt(paper_id, out_net, in_net,facet=None):
    print '\n\n.....generating graph_txt_file for '+ paper_id + '.....'
    g = gen_ind_graph(paper_id, out_net, in_net,facet)
    if facet:
        name = "Walker/graph/cos/" + paper_id +facet + '_graph_cos.txt'
    else:
        name = "Walker/graph/cos/" + paper_id + '_graph_cos.txt'
        
    file = open(name, 'w')
    for item in g:
        item_str = item[0]+'\t'+item[1]+'\t'+str(item[2])+'\n'
        #print item_str
        file.write(item_str)
    file.close()

    file = open('Walker/graph/cos/'+paper_id+'_seed.txt', 'w')
    file.write(paper_id)
    file.close()


# In[120]:

# Loading dict_out_cit_facet  and dict_in_cit_facet
print '....loading dict_out_cit_facet in pickled.....'
with open("pickled/dict_out_cit_facet_ml=0.2_deep_5k.txt", "rb") as dict_file:
    outcite_2 = pickle.load(dict_file)

print '....loading dict_in_cit_facet in pickled.....'
with open("pickled/dict_in_cit_facet_ml=0.2_deep_5k.txt", "rb") as dict_file:
    incite_2 = pickle.load(dict_file)




#### Select the paper/papers to generate graph for

paper_id = 'A00-1005'
get_graph_txt(paper_id, outcite_2, incite_2, 'C')


## Use this part to generate graphs for a group of paper
#for i in xrange(10):
#    get_graph_txt(paper_array[i], outcite_2, incite_2,'M')
  
















