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
    
    # Create log file if it doesn't exist and print a message
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

if 'show_report_page' not in st.session_state:
    st.session_state.show_report_page = False

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
            st.rerun()
        else:
            st.error("Invalid username or password.")
else:
    # Check if we need to show the report page
    if st.session_state.show_report_page:
        # Report Page
        st.title("Report Page")
        logs = read_logs()
        
        if not logs.empty:
            st.dataframe(logs)
            print("Displayed log table with entries.")
        else:
            st.write("No logs available.")
        
        # Button to return to the main uploader page
        if st.button("Back to Uploader"):
            st.session_state.show_report_page = False  # Reset flag for main page
            # Force rerun to go back to main page
            st.rerun()
    else:
        # Main app content after login
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

                elif uploaded_file.name.endswith(('.jpg', '.jpeg', '.png')):
                    st.write("Image Data: ", uploaded_file.name)

                else:
                    st.write("File uploaded successfully but not recognized as a CSV or image.")

                # Log results after processing successfully
                log_results(model_type, core_option, uploaded_file.name, dataset_size)

                # Display selected model type and core option only after Run button is clicked and file is uploaded
                if uploaded_file and run_button_clicked:
                    st.write(f"Model Type: {model_type}")
                    st.write(f"Core Option: {core_option}")

                    # Button to navigate to the report page
                    if st.button("View Report"):
                        st.session_state.show_report_page = True  # Set flag for report page display
                        st.experimental_rerun()  # Rerun the app to show the report page
