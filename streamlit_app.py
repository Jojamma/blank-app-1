import streamlit as st
import pandas as pd
import datetime
import os

# Hardcoded credentials for demonstration (use a secure method in production)
USERNAME = "admin"
PASSWORD = "password"

# Function to check credentials
def check_credentials(username, password):
    return username == USERNAME and password == PASSWORD

# Function to log results to a file
def log_results(model_type, core_option, uploaded_file_name, dataset_size):
    log_entry = f"{datetime.datetime.now()}, Model Type: {model_type}, Core Option: {core_option}, Uploaded File: {uploaded_file_name}, Dataset Size: {dataset_size}\n"
    
    # Create log file if it doesn't exist
    if not os.path.exists("upload_log.txt"):
        with open("upload_log.txt", "w") as log_file:
            log_file.write(log_entry)
        print("Created upload_log.txt and added the first entry.")
    else:
        with open("upload_log.txt", "a") as log_file:
            log_file.write(log_entry)
        print(f"Updated upload_log.txt with new entry: {log_entry.strip()}")

# Function to read logs from the file
def read_logs():
    try:
        # Read logs from the file into a DataFrame
        logs = pd.read_csv("upload_log.txt", sep=",", header=None, names=["Timestamp", "Model Type", "Core Option", "Uploaded File", "Dataset Size"])
        return logs
    except FileNotFoundError:
        return pd.DataFrame(columns=["Timestamp", "Model Type", "Core Option", "Uploaded File", "Dataset Size"])

# Initialize session states if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Uploader"

# Login page logic
if not st.session_state.logged_in:
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if check_credentials(username, password):
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
            # Use st.rerun() to refresh the app state
            st.experimental_rerun()
        else:
            st.error("Invalid username or password.")
else:
    # Sidebar navigation menu
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to:", ["Uploader", "Dashboard"])
    st.session_state.current_page = page

    if st.session_state.current_page == "Uploader":
        # Main app content for uploading files
        st.title("Large File Uploader")

        # File uploader for dataset
        uploaded_file = st.file_uploader("Upload your dataset (supports large files up to 50GB)", type=None)

        # Dropdown for model type selection
        model_type = st.selectbox("Select Model Type:", ["Transformer", "CNN", "RNN"])

        # Dropdown for core options selection
        core_option = st.selectbox("Select Core Option:", ["CPU", "GPU", "HDFS"])

        # Button to process the uploaded file
        run_button_clicked = st.button("Run")

        if run_button_clicked:
            if uploaded_file is None:
                # Display an error message if no file is uploaded after clicking Run
                st.error("Please upload a valid file before running.")
            else:
                # Process the uploaded file only after clicking Run and uploading a file
                dataset_size = uploaded_file.size  # Get size of the uploaded file in bytes

                if uploaded_file.name.endswith('.csv'):
                    try:
                        # Read and process CSV in chunks to avoid memory issues
                        chunk_size = 10 ** 6  # Adjust chunk size as needed
                        column_names = None

                        for chunk in pd.read_csv(uploaded_file, chunksize=chunk_size):
                            if column_names is None:
                                column_names = chunk.columns.tolist()  # Get column names from first chunk

                    except Exception as e:
                        st.error(f"Error reading CSV file: {e}")

                elif uploaded_file.name.endswith(('.jpg', '.jpeg', '.png')):
                    pass  # Handle image files here

                else:
                    pass  # Handle other unsupported file types here

                # Log results after processing successfully
                log_results(model_type, core_option, uploaded_file.name, dataset_size)

                # Display selected model type and core option only after Run button is clicked and file is uploaded
                if uploaded_file and run_button_clicked:
                    st.write(f"Model Type: {model_type}")
                    st.write(f"Core Option: {core_option}")

    elif st.session_state.current_page == "Dashboard":
        # Dashboard Page Logic
        st.title("Dashboard")

        logs = read_logs()

        if logs.empty:
            st.write("No data available.")
        else:
            # Display key metrics
            total_files_processed = len(logs)
            total_dataset_size = logs["Dataset Size"].sum()
            most_used_model_type = logs["Model Type"].mode()[0] if not logs["Model Type"].empty else "N/A"

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Files Processed", total_files_processed)
            col2.metric("Total Dataset Size (bytes)", total_dataset_size)
            col3.metric("Most Used Model Type", most_used_model_type)

            # Visualization: Bar chart of model usage counts
            model_usage_counts = logs["Model Type"].value_counts()
            st.bar_chart(model_usage_counts)
