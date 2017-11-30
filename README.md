# FeRoSA: Faceted Recommendation System for Scientific Articles

## Introduction

A​ ​smart​ ​recommendation​ ​engine​ ​should​ ​be​ ​able​ ​to​ ​organize​ ​the​ ​recommended papers​ ​into​ ​multiple​ ​facets/tags​ ​such​ ​as​ ​background,​ ​alternative​ ​approaches, methods​ ​and​ ​comparison. 

This module uses​ ​the​ ​AAN​ ​dataset​ ​which​ ​is​ ​an​ ​assemblage​ ​of​ ​all​ ​papers​ ​included​ ​in ACL2​ ​publication​ ​venue​ ​and​ ​categorize​ ​the​ ​citation​ ​links​ ​based​ ​on​ ​their occurrence​ ​in​ ​various​ ​sections​ ​of​ ​the​ ​paper. 


## Overview:

This module can be used to run two types of experiments:

- Recommend relevant papers(scientific articles) to user for a given 'search-paper'.

- Recommend relevant papers(scientific articles) to user for a given 'search-paper' and 'relation to the search-paper'.

Examples of both experiments are described in more detail below.

## Content:

This is the open repository for the 'Faceted Recommendation System for Scientific Articles':

1) '/Walker'
Contains the 'Walker' module developed by- 'Zhang H, Schaefer M, Crawford J, Kiel C, Serrano L, and Cowen LJ' and also available on this <a href="https://github.com/TuftsBCB/Walker">github_repository</a>.<br>
 
2) '/pickled'
Will(..once all codes are run) contain the intermediate pickled files, which will later be used for graph-generation and paper-prediction. "The user does not specifically need to understand this directory to run experiments..!!! "

3) '/cos_5k'
Similar to '/pickled'. Will contain data related to cosine-similarity of the papers. 

4) '/lda_5k'
Similar to '/pickled'. Will contain data related to LDA-topic-modeling.

5) '/report.pdf'
Can be used by the user for better understanding of the system architecture.

6) 'section_mapping.ods'
Contains mapping from 'Headings (in paper)' -to- 'Possible Relation' among ("C":comparison, "M":method, "RW":related work )


## Execution:

### Step-1: Creating the Working Directory
Create a working directory "/ferosa".<br><br>
Inside "/ferosa", create:
- "/ferosa/code" : to contain all the items of this repository

Next we will download our data in:
- "/ferosa/text_data" :to store text data of all papers
- "/ferosa/xml_data" :to store xml data of all papers


### Step-2: Downloading the Data
1) To download the AAN(ACL Anthology Network) text_data:

- Go to the Website = "http://clair.eecs.umich.edu/aan/index.php" 
....or use the <a href="http://clair.eecs.umich.edu/aan/downloads/aandec2014.tar.gz">direct_link</a> to download the zip file.

- Extract the contents of "aandec2014.tar.gz" which generates a folder "2014".
-->Rename "2014" to "text_data" and make sure it is placed in "/ferosa" directory.


2) To download the ACN(ACL Anthology Network) xml_data:

- Go to the Website at: http://acl-arc.comp.nus.edu.sg and download the 'ParsCit Structured XML'(Version 20160301).
....or use the following terminal command(from the "/ferosa" directory) to download all the zipped files at once.

`wget -r -np -nH --cut-dirs=1 -R index.html http://acl-arc.comp.nus.edu.sg/archives/acl-arc-160301-parscit/`
This downloads a folder 'acl-arc-160301-parscit/' containing a lot of zipped files.

- From inside the 'acl-arc-160301-parscit/' folder use the following command to extract all the zipped files into "ferosa/xml_data" (while also stripping the leading directory of the zipped files) .

`for f in *.tgz; do tar xvzf $f --strip=1 -C ../xml_data; done `

### Step-3: Installing dependencies/python modules
Following python modules will be required to successfully run all the codes: 

`sklearn numpy pandas pickle distance re ezodf timeit stop_words threading lxml nltk gensim logging`

### Step-4: Step-by-Step Execution
------The long file names are NOT a prerequisite to run the codes, change them if you like shorter names------

1) `gen_init_cit_net.py` - run to generate initial citation network. Generates incite (outcite) dictionary, where "key=paper_id, value = list of paper_id's that belong to incite (outcite) of the key"

2) `gen_cit_head_threading_deep.py` - run to analyze the parsed xml's of the papersand generate a "dictionary-of-dictionary" type network. Here for Outer_dict, "key=paper_id, value=Inner_dict" and for Inner_dict, "key= headings (of key of Outer_dict), value = list of papers cited under the key as heading".

3) `gen_dict_cit_head_5k.py` - run to strip down the network size by thresholding the minimum no. of citation links for a paper to exist in the network. To change the threshold value use the MIN_CIT_LINKS var at the top of the file. By default, MIN_CIT_LINKS=10 which results in a stripped down citation network containing only 4536 papers. 

4) `gen_cit_facet_threading_deep_5k_secmap.py` - maps the Heading (from dictionary of the above step) to its corresponding relation "C","M","RE" and "RW" (from section_mapping.ods ).

5) `cosine_similarity.py` - run to generate the cosine_similarity matrix for the the papers (using the text data available). 

6) `lda_5k.py` - run to generate the distance matrix for the papers (using the text data available). Jensen-Shannon is used as the distance metric where distance is computed between topic distribution of the document.

### Step-5 Generating Results

#### For Cosine-similarity based prediction
1) `generate_graph_txt_cos.py` - Change the last line/section of code to select the paper/papers for which graph is to be generated. Then run the code to generate corresponding graph file(.. and a seed file) in "Walker/graph/cos/".
Note: If using the paper_id/paper_code directly(rather than the index) then make sure that code exists in "paper_array_5k.txt".

2) From inside the folder "Walker/", run the command `python run_walker.py <PAPER_ID><REL_CODE>_graph_cos.txt graph/cos/<PAPER_ID>_seed.txt`.
Where, 
PAPER_ID = 8 character code available in "paper_array_5k.txt" (The mapping for paper_id and paper_name can be found in "ferosa/text_data/paper_ids.txt")
REL_CODE = 'C' --> Comparison | 'M' --> Method | 'RE' --> Results | 'RW' --> RelatedWork

e.g.  `python run_walker.py A00-1009M_graph_cos.txt graph/cos/A00-1009_seed.txt`

#### For Jensen-Shannon-distance based prediction
1) `generate_graph_txt_jsd.py` - Change the last line/section of code to select the paper/papers for which graph is to be generated. Then run the code to generate corresponding graph file(..and a seed file) in "Walker/graph/jsd/". 
Note: If using the paper_id/paper_code directly(rather than the index) then make sure that code exists in "paper_array_5k.txt".

2) From inside the folder "Walker/", run the command `python run_walker.py <PAPER_ID><REL_CODE>_graph_jsd.txt graph/jsd/<PAPER_ID>_seed.txt`.
Where, 
PAPER_ID = 8 character code available in "paper_array_5k.txt" (The mapping for paper_id and paper_name can be found in "ferosa/text_data/paper_ids.txt")
REL_CODE = 'C' --> Comparison | 'M' --> Method | 'RE' --> Results | 'RW' --> RelatedWork

e.g.  `python run_walker.py A00-1009M_graph_jsd.txt graph/jsd/A00-1009_seed.txt`

## EXTRA:
1) 'paper_array_5k.txt'
List of papers that are available for testing (i.e. that are present in the stripped down 5k-dataset). While generating results (Step-5), only use these paper_id's.

2) 'xml_prob_array.txt'
List of papers, for which the XML file might be broken (almost 30-40 papers). I this case user might experience some XML-error while running `gen_cit_head_threading_deep.py`
Solution-- 
           a) Manually rectify the XML files
           b) Uncomment Ln98-Ln104 in `gen_cit_head_threading_deep.py` to ignore such files



