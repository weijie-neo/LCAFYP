import streamlit as st
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import brightway2 as bw
from brightway2 import *
from bw2data.parameters import ActivityParameter, DatabaseParameter, ProjectParameter, Group
import time


def submit_form():
    with st.form(key='my_form'):
        uploaded_file_name = st.text_input(label='Enter some text')
        uploaded_file = st.file_uploader("Upload your file")
        submitted = st.form_submit_button(label='Submit')
        if submitted:
            df = pd.read_excel(uploaded_file)
            save_uploadedfile(uploaded_file,uploaded_file_name)





def save_uploadedfile(uploadedfile,uploaded_file_name):
    with open(os.path.join("tempDir",uploaded_file_name+'.xlsx'),"wb") as f:
        f.write(uploadedfile.getbuffer())
    return st.success("Saved File:{} to tempDir".format(uploaded_file_name))


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

pages = ["Create a Project", "View a Project", "Delete a Project"]
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

if option == pages[2]:
    st.header(option)
    choose_file()   
    delete_button() 
    