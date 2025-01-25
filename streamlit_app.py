import streamlit as st
import pandas as pd
import datetime
import os

# Hardcoded credentials for demonstration (use a secure method in production)
USERNAME = "admin"
PASSWORD = "jogu@2003"

# Function to check credentials
def check_credentials(username, password):
    return username == USERNAME and password == PASSWORD

# Initialize session states if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Login page logic
if not st.session_state.logged_in:
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if check_credentials(username, password):
            st.session_state.logged_in = True
        else:
            st.error("Invalid username or password.")
else:
    st.title("Dataset Uploader and Model Selector")

    # File uploader for dataset
    uploaded_file = st.file_uploader("Upload your dataset (supports large files up to 50GB)", type=["csv"])

    model_type = st.selectbox("Select Model Type:", ["Transformer", "CNN", "RNN", "ANN"])
    core_option = st.selectbox("Select Core Option:", ["CPU", "GPU", "HDFS"])

    run_button_clicked = st.button("Run")

    if run_button_clicked:
        if uploaded_file is None:
            # Display an error message if no file is uploaded after clicking Run
            st.error("Please upload a valid file before running.")
        else:
            dataset_size = uploaded_file.size  # Get size of the uploaded file in bytes

            try:
                # Display column names for CSV files
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                    st.write(f"Uploaded Dataset Columns: {list(df.columns)}")
                else:
                    st.error("Unsupported file type. Please upload a CSV file.")

                # Display features based on the selected model type
                st.write("### Selected Features:")
                if model_type == "Transformer":
                    st.write("- Epoch")
                    st.write("- Batch Size")
                    st.write("- Iteration")
                    st.write("- Learning Rate")
                    st.write("- Attention Mechanism")
                elif model_type == "CNN":
                    st.write("- Epoch")
                    st.write("- Batch Size")
                    st.write("- Iteration")
                    st.write("- Learning Rate")
                    st.write("- Convolutional Layers")
                elif model_type == "RNN":
                    st.write("- Epoch")
                    st.write("- Batch Size")
                    st.write("- Iteration")
                    st.write("- Learning Rate")
                    st.write("- Hidden States")
                elif model_type == "ANN":
                    st.write("- Epoch")
                    st.write("- Batch Size")
                    st.write("- Iteration")
                    st.write("- Learning Rate")
                    st.write("- Activation Functions")

                # Display selected model type and core option only after Run button is clicked and file is uploaded
                st.write(f"Model Type: {model_type}")
                st.write(f"Core Option: {core_option}")

            except Exception as e:
                st.error(f"Error processing the uploaded file: {e}")
