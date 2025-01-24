import streamlit as st
import pandas as pd
import os

# Title of the app
st.title("Model Runner")

# File uploader for dataset with no size restriction
uploaded_file = st.file_uploader("Upload your dataset (CSV or image files)", type=['csv', 'jpg', 'jpeg', 'png'], accept_multiple_files=False)

# Dropdown for model type selection
model_type = st.selectbox("Select Model Type:", ["Transformer", "CNN", "RNN"])

# Dropdown for core options selection
core_option = st.selectbox("Select Core Option:", ["CPU", "GPU", "HDFS"])

# Button to run the model
if st.button("Run"):
    if uploaded_file is not None:
        # Check if the uploaded file is a CSV
        if uploaded_file.name.endswith('.csv'):
            try:
                # Read the CSV file
                df = pd.read_csv(uploaded_file)
                attributes = df.columns.tolist()
                st.write("CSV Attributes:", attributes)
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")
        
        # Check if the uploaded file is an image (based on extensions)
        elif uploaded_file.name.endswith(('.jpg', '.jpeg', '.png')):
            st.write("Image Data: ", uploaded_file.name)
        
        else:
            st.write("Unsupported file type.")
    
    # Display selected model type and core option
    st.write(f"Model Type: {model_type}")
    st.write(f"Core Option: {core_option}")

