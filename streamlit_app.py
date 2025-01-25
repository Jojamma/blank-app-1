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

# Function to log results to a file
def log_results(model_type, core_option, uploaded_file_name, dataset_size):
    # Set CPU, GPU, HDFS usage based on core option
    cpu_usage = 1 if core_option == "CPU" else 0
    gpu_usage = 1 if core_option == "GPU" else 0
    hdfs_usage = 1 if core_option == "HDFS" else 0

    # Create a log entry (consistent format with no extra commas)
    log_entry = f'"{datetime.datetime.now()}", "{uploaded_file_name}", "{dataset_size}", "{model_type}", {cpu_usage}, {gpu_usage}, {hdfs_usage}\n'

    try:
        # Create log file if it doesn't exist
        if not os.path.exists("upload_log.txt"):
            with open("upload_log.txt", "w") as log_file:
                log_file.write("Timestamp,Dataset Name,Dataset Size,Model Used,CPU,GPU,HDFS\n")  # Header row
                log_file.write(log_entry)
        else:
            with open("upload_log.txt", "a") as log_file:
                log_file.write(log_entry)

        # Debugging: Confirm log entry is written
        st.write(f"Log entry written: {log_entry}")  # Debug message to show what was written

    except Exception as e:
        st.error(f"Error writing to log file: {e}")

# Function to read logs from the file (disable caching for fresh data)
def read_logs():
    try:
        if not os.path.exists("upload_log.txt"):
            st.write("Log file not found!")
            return pd.DataFrame(columns=["Timestamp", "Dataset Name", "Dataset Size", "Model Used", "CPU", "GPU", "HDFS"])

        # Explicitly disable caching to ensure fresh data is read
        logs = pd.read_csv("upload_log.txt", on_bad_lines='skip')

        if logs.empty:
            st.write("Log file is empty!")
            return pd.DataFrame(columns=["Timestamp", "Dataset Name", "Dataset Size", "Model Used", "CPU", "GPU", "HDFS"])

        return logs

    except Exception as e:
        st.error(f"Error reading logs: {e}")
        return pd.DataFrame(columns=["Timestamp", "Dataset Name", "Dataset Size", "Model Used", "CPU", "GPU", "HDFS"])

# Initialize session states if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'current_page' not in st.session_state:
    st.session_state.current_page = ""

# Logic to refresh the page after file upload
def refresh_page():
    st.session_state.current_page = "Uploader" if st.session_state.current_page == "Log Results" else "Log Results"

# Login page logic
if not st.session_state.logged_in:
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if check_credentials(username, password):
            st.session_state.logged_in = True
            # Set the current page to "Uploader" after login
            st.session_state.current_page = "Uploader"
        else:
            st.error("Invalid username or password.")
else:
    # Sidebar navigation menu
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to:", ["Uploader", "Log Results"])

    # Set current page based on the sidebar selection
    st.session_state.current_page = page

    if page == "Uploader":
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

                    # Log results after processing successfully
                    log_results(model_type, core_option, uploaded_file.name, dataset_size)

                    # Refresh the page to update logs
                    refresh_page()

                    # Display selected model type and core option only after Run button is clicked and file is uploaded
                    st.write(f"Model Type: {model_type}")
                    st.write(f"Core Option: {core_option}")

                except Exception as e:
                    st.error(f"Error processing the uploaded file: {e}")

    elif page == "Log Results":
        st.title("Log Results")

        # Force re-reading logs every time the page loads
        logs = read_logs()

        if not logs.empty:
            # Reverse the order to display the most recent logs at the top
            logs = logs.iloc[::-1].reset_index(drop=True)

            st.subheader("Log Table")
            
            # Ensure the whole log file is displayed by adjusting height dynamically
            table_height = min(800, max(300, logs.shape[0] * 20))  # Adjust height dynamically
            st.dataframe(logs, height=table_height)
        else:
            st.write("No logs available.")
