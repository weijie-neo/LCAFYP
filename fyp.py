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
    choose_file.var = st.selectbox(
     'Project',
     (list))

def delete_button():
    m = st.markdown("""
    <style>
    div.stButton > 
        button:first-child {
            background-color: #FF0000;
            color:#ffffff;
            }
    
    </style>""", unsafe_allow_html=True)

    if st.button('Delete'):
        os.remove('tempDir/' + choose_file.var)
        time.sleep(1)
        st.write('File Deleted, please refresh to view changes')


    

def LCA_tool():
    
    database = st.selectbox('Select your database',['forwast','biosphere3','ecoinvent'])
    selected = Database(database).search("*", limit=None)
    options = st.multiselect(
    'Search for an Activity',
    selected)
    
    myMethods = [method for method in bw.methods
             if "ReCiPe" in method[0] 
             and "(H,A)" in method[0] 
             and "w/o" not in method[0] 
             and "total" not in method[1]
             and "total" in method[2]]
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
            x = 'Method',y='Score',hue='Name'
        )
        
        st.pyplot(g)





pages = ["Create a Project", "TEST View a Project", "Delete a Project"]

bw.projects.set_current("StepByStep")
bw.bw2setup()
if "forwast" not in bw.databases:
    filepath = download_file("forwast.bw2package.zip", url="http://lca-net.com/wp-content/uploads/")
    dirpath = os.path.dirname(filepath)
    zipfile.ZipFile(filepath).extractall(dirpath)
    bw.BW2Package.import_file(os.path.join(dirpath, "forwast.bw2package"))

if 'ecoinvent' in bw.databases:
    print("Database has already been imported.")
else:
    # mind that the ecoinvent file must be unzipped; then: path to the datasets subfolder
    fpei35cut = r"C:\Users\weiji\Desktop\mycode\ecoinvent"
    # the "r" makes sure that the path is read as a string - especially useful when you have spaces in your string
    ei35cut = bw.SingleOutputEcospold2Importer(fpei35cut, 'ecoinvent')
    ei35cut
    ei35cut.apply_strategies()
    ei35cut.statistics()
bioDB = bw.Database("biosphere3")
forwastDB = bw.Database("forwast")
eiDB = bw.Database('ecoinvent')
forwastDB.make_searchable()
eiDB.make_searchable()
option = st.sidebar.selectbox(
    '',
    (pages)
)

if option == pages[0]:
    st.header(option)
    submit_form()
if option == pages[1]:
    st.header(option)
    choose_file()
    df = pd.read_excel('tempDir/' + choose_file.var )
    st.write(df)
    LCA_tool()
if option == pages[2]:
    st.header(option)
    choose_file()   
    delete_button() 
    

