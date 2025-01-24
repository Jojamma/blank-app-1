import streamlit as st
import pandas as pd
import os

# Title of the app
st.title("Model Runner")

# Input for dataset path
dataset_path = st.text_input("Dataset Path:")

# Dropdown for model type selection
model_type = st.selectbox("Select Model Type:", ["Transformer", "CNN", "RNN"])

# Dropdown for core options selection
core_option = st.selectbox("Select Core Option:", ["CPU", "GPU", "HDFS"])

# Button to run the model
if st.button("Run"):
    if dataset_path.endswith('.csv'):
        # If it's a CSV file, read and display its attributes
        try:
            df = pd.read_csv(dataset_path)
            attributes = df.columns.tolist()
            st.write("CSV Attributes:", attributes)
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")
    elif os.path.isdir(dataset_path):
        # If it's a directory, assume it's image data and print folder name
        folder_name = os.path.basename(dataset_path)
        st.write(f"Image Data Folder: {folder_name}")
    else:
        # If it's not a recognized format
        st.write("Image Data")

    # Here you would add the logic to run your model based on the inputs
    # For demonstration purposes, we just display the inputs
    st.write(f"Model Type: {model_type}")
    st.write(f"Core Option: {core_option}")

