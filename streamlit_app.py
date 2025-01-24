
import streamlit as st
import pandas as pd
import os

# Title of the app
st.title("Large File Uploader")

# File uploader for dataset
uploaded_file = st.file_uploader("Upload your dataset (supports large files up to 50GB)", type=None)

# Dropdown for model type selection
model_type = st.selectbox("Select Model Type:", ["Transformer", "CNN", "RNN"])

# Dropdown for core options selection
core_option = st.selectbox("Select Core Option:", ["CPU", "GPU", "HDFS"])

# Button to process the uploaded file
if st.button("Run"):
    if uploaded_file is not None:
        # Check if the uploaded file is a CSV
        if uploaded_file.name.endswith('.csv'):
            try:
                # Read and process CSV in chunks to avoid memory issues
                st.write("Processing CSV file...")
                chunk_size = 10 ** 6  # Adjust chunk size as needed
                column_names = None
                
                for chunk in pd.read_csv(uploaded_file, chunksize=chunk_size):
                    if column_names is None:
                        column_names = chunk.columns.tolist()  # Get column names from the first chunk
                    st.write(f"Processed a chunk with {len(chunk)} rows.")
                
                # Display column names after processing all chunks
                st.write("CSV Column Names:", column_names)
                
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")
        
        # Check if it's an image or other file types
        elif uploaded_file.name.endswith(('.jpg', '.jpeg', '.png')):
            st.write("Image Data: ", uploaded_file.name)
        
        else:
            st.write("File uploaded successfully but not recognized as a CSV or image.")

    else:
        st.error("Please upload a valid file.")

    # Display selected model type and core option
    st.write(f"Model Type: {model_type}")
    st.write(f"Core Option: {core_option}")
