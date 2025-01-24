import streamlit as st
import pandas as pd
import datetime

# Hardcoded credentials for demonstration (use a secure method in production)
USERNAME = "admin"
PASSWORD = "password"

# Function to check credentials
def check_credentials(username, password):
    return username == USERNAME and password == PASSWORD

# Function to log results to a file
def log_results(model_type, core_option, uploaded_file_name):
    log_entry = f"{datetime.datetime.now()}: Model Type: {model_type}, Core Option: {core_option}, Uploaded File: {uploaded_file_name}\n"
    with open("upload_log.txt", "a") as log_file:
        log_file.write(log_entry)

# Function to read logs from the file
def read_logs():
    try:
        # Read logs from the file into a DataFrame
        logs = pd.read_csv("upload_log.txt", sep=":", header=None, names=["Timestamp", "Details"])
        return logs
    except FileNotFoundError:
        return pd.DataFrame(columns=["Timestamp", "Details"])

# Initialize session states if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'show_log_page' not in st.session_state:
    st.session_state.show_log_page = False

if 'run_clicked' not in st.session_state:
    st.session_state.run_clicked = False

# Login page logic
if not st.session_state.logged_in:
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if check_credentials(username, password):
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
            # Force rerun to show the main app page
            st.experimental_rerun()
        else:
            st.error("Invalid username or password.")
else:
    # Check if we need to show the log page
    if st.session_state.show_log_page:
        # Log Table Page
        st.title("Log Table")
        logs = read_logs()
        
        if not logs.empty:
            st.dataframe(logs)
        else:
            st.write("No logs available.")
        
        # Button to return to the main page
        if st.button("Back to Main"):
            st.session_state.show_log_page = False
            # Force rerun to go back to main page
            st.experimental_rerun()
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
        if uploaded_file and st.button("Run"):
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

            # Set session state flag when Run button is clicked
            st.session_state.run_clicked = True

        elif not uploaded_file:
            st.error("Please upload a valid file.")

        # Display selected model type and core option
        if uploaded_file:
            st.write(f"Model Type: {model_type}")
            st.write(f"Core Option: {core_option}")

        # Conditionally display Log Results button only after Run is clicked
        if uploaded_file and st.session_state.run_clicked:
            if st.button("Log Results"):
                log_results(model_type, core_option, uploaded_file.name)
                st.success("Results logged successfully!")  # Corrected line

