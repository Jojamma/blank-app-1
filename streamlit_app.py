import streamlit as st
import pandas as pd

# Title of the app
st.title("Large File Uploader")

# File uploader for dataset
uploaded_file = st.file_uploader("Upload your dataset (supports large files up to 50GB)", type=None)

# Dropdown for model type selection
model_type = st.selectbox("Select Model Type:", ["Transformer", "CNN", "RNN"])

# Dropdown for core options selection
core_option = st.selectbox("Select Core Option:", ["CPU", "GPU", "HDFS"])

# Input for chunk size configuration
chunk_size = st.number_input("Select Chunk Size:", min_value=1000, max_value=10**7, value=10**6)

# Button to process the uploaded file
if st.button("Run"):
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            try:
                st.write("Processing CSV file...")
                chunk_list = []
                
                with st.spinner("Processing..."):
                    for chunk in pd.read_csv(uploaded_file, chunksize=chunk_size):
                        chunk_list.append(chunk)
                        st.write(f"Processed a chunk with {len(chunk)} rows.")
                
                # Display column names after processing all chunks
                column_names = chunk_list[0].columns.tolist() if chunk_list else []
                st.write("CSV Column Names:", column_names)
                
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")
        
        elif uploaded_file.name.endswith(('.jpg', '.jpeg', '.png')):
            st.write("Image Data: ", uploaded_file.name)
        
        else:
            st.write("File uploaded successfully but not recognized as a CSV or image.")

    else:
        st.error("Please upload a valid file.")

    # Display selected model type and core option
    st.write(f"Model Type: {model_type}")
    st.write(f"Core Option: {core_option}")
