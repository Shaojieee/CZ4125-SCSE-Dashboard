# Nanyang Technological University SCSE Dashboard


The information used in this project is sourced from Google Scholar.



This project consists of 2 main folders.
1. `data_sources` contains all the code related to scraping and data processing.
2. `streamlit` contains the code to build the dashboard.

### `data_sources`
The notebooks in this directory are numbered from 1 to 8 which signifies the code that has to be run first.
1 to 4 are mainly data extraction from Google Scholar. 5 to 8 are used to process and transform the data.

#### Data Storage
The folders are used to store the data extracted. 

The filename for the google scholar files is the `user` value in the Google Scholar profile URL. A mapping from name to the user id can be found in  the files located in `data_sources/processed`.

Simiarly for dr ntu files, the filename is the unique user id in the dr ntu profile URL. The mapping from name to the dr ntu id can be found in`data_sources/processed/scse_profile.csv`.

#### Data Processing
Basic data cleaning is performed, such as replace `None` values.

GPT is used as well to try to extract details from the publications and the faculty biography. **Due to cost issue, only publications from 2022 and 2023 are processed using GPT.**

The use of GPT helps us to extract information such as the publication topics. This can greatly help us in grouping the professors according to their interests. However, the results from GPT is not ideal. Better prompting can be done. 

### `streamlit`

The dashboard consist mainly simple statistics, collaboration network as well as the research focus.

Through the use of statistics like h-index we are able to measure the professors productivity and impact over the years. 

Through the collaboration network, we are able to visualise how well connected is a professor. We can view whether the collaboration is recent.

Lastly, using the research topic we obtained from GPT, we are able to better identify Professors research focus and also compare within the different professors.

