from random import choices
import streamlit as st
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import brightway2 as bw
from brightway2 import *
from bw2data.parameters import ActivityParameter, DatabaseParameter, ProjectParameter, Group
import time
import zipfile
import os
from bw2data.utils import download_file
import seaborn as sns


def submit_form():  #need to add prevent duplicate
    with st.form(key='my_form'):
        uploaded_file_name = st.text_input(label='Name your Project')
        uploaded_file = st.file_uploader("Upload your file")
        submitted = st.form_submit_button(label='Submit')
        if submitted and uploaded_file is not None and uploaded_file_name != '':
            df = pd.read_excel(uploaded_file)
            save_uploadedfile(uploaded_file,uploaded_file_name)
        elif submitted and uploaded_file_name == '':
            st.write('Please name your project!')
        elif submitted and uploaded_file is  None:
            st.write('Please upload your file!')



def save_uploadedfile(uploadedfile,uploaded_file_name):
    with open(os.path.join("tempDir",uploaded_file_name+'.xlsx'),"wb") as f:
        f.write(uploadedfile.getbuffer())
    return st.success("Saved File: {} to tempDir".format(uploaded_file_name))


def choose_file():
    list = os.listdir(os.getcwd() + '/tempDir')
    choose_file = st.selectbox(
     'Project',
     (list))
    global filename
    filename.append(choose_file)


def choose_multiple_files():
    list = os.listdir(os.getcwd() + '/tempDir')
    choose_file = st.multiselect(
     'Project',
     (list))
    global filename
    for i in choose_file:
        filename.append(i)
    
    
    
    
def delete_button(filename):
    m = st.markdown("""
    <style>
    div.stButton > 
        button:first-child {
            background-color: #FF0000;
            color:#ffffff;
            }
    
    </style>""", unsafe_allow_html=True)

    if st.button('Delete'):
        os.remove('tempDir/' + filename)
        time.sleep(1)
        st.write('File Deleted, please refresh to view changes')


def mapper(filename,multiselect):
    datasets = pd.DataFrame() 
    for f in filename:
        
        data = pd.read_excel(os.getcwd() + '/tempDir/' + f)
        data['type'] = f
        datasets = datasets.append(data)
    
    ei_db_df = datasets.loc[datasets['Database name'] == 'ecoinvent 3.5_cutoff_ecoSpold02']
    
    DB = bw.Database('ecoinvent 3.5_cutoff_ecoSpold02')
    DB.make_searchable()
    myMethods = multiselect
    results = []

    ei_db_df = ei_db_df[['Quantity','Market name','Phase','type']]

    for i in ei_db_df.values:
        
        lci = bw.Database('ecoinvent 3.5_cutoff_ecoSpold02').search(str(i[1]))
        lci = lci[0]
        lca = bw.LCA({lci:1})
        lca.lci() 
        for method in myMethods:         
            lca.switch_method(method)
            lca.lcia()
            results.append((lci["name"], method[1].title(),lca.score,i[0], lca.score * i[0], i[2],i[3]))
    
    
    lca_df = pd.DataFrame(results, columns=["Name", "Method", "Score/Unit","Quantity","Score","Phase","type"])
    global raw_results_df 
    raw_results_df = lca_df
    sns.set(rc={'figure.figsize':(50,20)})
    
def methodchoice():
    options = st.multiselect(
     'Methods',
     (bw.methods))
    global multiselect
    for i in options:
        multiselect.append(i)
    

def single_viz(raw_results_df):
    results_df = pd.pivot_table(raw_results_df, columns = "Method", values = "Score", aggfunc=np.sum)
    results_2_df = pd.pivot_table(raw_results_df, index = "Phase", columns = "Method", values = "Score", aggfunc=np.sum)
    st.title('Result')
    st.header('Grouped by Method')
    
    g = sns.catplot(
                data = raw_results_df,
                kind='bar',
                x = 'Method' ,y='Score', 
                ci=None , estimator=sum
                )      
         
    st.pyplot(g)
    st.write(results_df)
    st.header('Grouped by Phase')
    
    g = sns.catplot(
                data = raw_results_df,
                kind='bar',
                x = 'Phase' ,y='Score', hue='Method',
                ci=None , estimator=sum
                )      
         
    st.pyplot(g)
    st.write(results_2_df)

def compare_viz(raw_results_df):
    
    results_df = pd.pivot_table(raw_results_df,index = "type",columns = "Method", values = "Score", aggfunc=np.sum)
    st.title('Result')
    st.header('Grouped by Type')
    g = sns.catplot(
                data = raw_results_df,
                kind='bar',
                x = 'type' ,y='Score', hue='Method',
                ci=None , estimator=sum
                )      
         
    st.pyplot(g)
    st.write(results_df)

    results_df = pd.pivot_table(raw_results_df,index = "type",columns = "Method", values = "Score", aggfunc=np.sum)
    
    st.header('Grouped by Method')
    g = sns.catplot(
                data = raw_results_df,
                kind='bar',
                x = 'Method' ,y='Score', hue='type',
                ci=None , estimator=sum
                )      
         
    st.pyplot(g)
    st.write(results_df)





def LCA_tool(multiselect):
    
    database = st.selectbox('Select your database',['forwast','biosphere3','ecoinvent 3.5_cutoff_ecoSpold02'])
    DB = bw.Database(database)
    DB.make_searchable()
    
    input = st.text_input('Search for market')
    selected = bw.Database(database).search(input, limit=None)
    if input is not '':
        options = st.multiselect(
        'Search for an Activity',
        selected)
    
    
        myMethods = multiselect
        results = []
        
        if options:
            for milk in options:
                lca = bw.LCA({milk:1})
                lca.lci()
                for method in myMethods:
                    lca.switch_method(method)
                    lca.lcia()
                    results.append((milk["name"], method[1].title(), lca.score))
            
            results_df = pd.DataFrame(results, columns=["Name", "Method", "Score"])
            results_df_pivot = pd.pivot_table(results_df, index = "Name", columns = "Method", values = "Score")
            st.write(results_df_pivot)

            g = sns.catplot(
                data = results_df,
                kind='bar',
                x = 'Method',y='Score',hue='Name',ci=None
            )
            
            st.pyplot(g)





pages = ["Create a Project","Search database", "View a Project", "Compare Projects", "Delete a Project"]

bw.projects.set_current("StepByStep")
bw.bw2setup()
if "forwast" not in bw.databases:
    filepath = download_file("forwast.bw2package.zip", url="http://lca-net.com/wp-content/uploads/")
    dirpath = os.path.dirname(filepath)
    zipfile.ZipFile(filepath).extractall(dirpath)
    bw.BW2Package.import_file(os.path.join(dirpath, "forwast.bw2package"))

if 'ecoinvent 3.5_cutoff_ecoSpold02' in bw.databases:
    print("Database has already been imported.")
else:
    # mind that the ecoinvent file must be unzipped; then: path to the datasets subfolder
    fpei35cut = r"C:/Users/weiji/Desktop/mycode/ecoinvent/datasets"
    # the "r" makes sure that the path is read as a string - especially useful when you have spaces in your string
    ei35cut = bw.SingleOutputEcospold2Importer(fpei35cut, 'ecoinvent 3.5_cutoff_ecoSpold02')
    ei35cut
    ei35cut.apply_strategies()
    ei35cut.statistics()
    ei35cut.write_database()


option = st.sidebar.selectbox(
    '',
    (pages)
)

if option == "Create a Project":
    st.header(option)
    submit_form()
if option ==  "View a Project":
    st.header(option)
    filename = []
    multiselect = []
    
    choose_file()
    
    for i in filename:
        data = pd.read_excel(os.getcwd() + '/tempDir/' + i)
        st.write(data)
    raw_results_df = pd.DataFrame() 
    methodchoice()
    
    if st.button('Run'):
        mapper(filename,multiselect)
        single_viz(raw_results_df)
       




if option == "Delete a Project":
    st.header(option)
    filename = [] 
    choose_multiple_files()
      
    delete_button(filename) 

if option == "Search database":
    st.header(option)
    multiselect = []
    methodchoice()
    LCA_tool(multiselect)

if option == "Compare Projects":
    st.header(option)
    filename = []
    multiselect = []
    choose_multiple_files()
    raw_results_df = pd.DataFrame() 
    methodchoice()
    if st.button('Run'):
        mapper(filename,multiselect)
        compare_viz(raw_results_df)
        