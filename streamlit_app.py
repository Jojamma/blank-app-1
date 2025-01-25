import streamlit as st
import pandas as pd
from datetime import datetime

# Hardcoded credentials for demonstration (use a secure method in production)
USERNAME = "admin"
PASSWORD = "jogu@2003"

# Function to check credentials
def check_credentials(username, password):
    return username == USERNAME and password == PASSWORD

# Initialize session states if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Initialize log data in session state
if 'log_data' not in st.session_state:
    st.session_state.log_data = []

# Login page logic
if not st.session_state.logged_in:
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if check_credentials(username, password):
            st.session_state.logged_in = True
            st.query_params = {"logged_in": "true"}  # Updated for new syntax
        else:
            st.error("Invalid username or password.")
else:
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Log Page"])

    if page == "Dashboard":
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
                dataset_name = uploaded_file.name

                # Log details into session state
                st.session_state.log_data.append({
                    "Dataset Name": dataset_name,
                    "Dataset Size": f"{dataset_size / (1024 * 1024):.2f} MB",
                    "Model": model_type,
                    "CPU": "Used" if core_option == "CPU" else "Not Used",
                    "GPU": "Used" if core_option == "GPU" else "Not Used",
                    "HDFS": "Used" if core_option == "HDFS" else "Not Used",
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

                st.success("Run executed and details logged successfully!")

    elif page == "Log Page":
        st.title("Log Page")
        st.write("This page logs all the model and dataset information during the session.")

        # Display Log Table
        if st.session_state.log_data:
            st.write("### Log Table")
            log_df = pd.DataFrame(st.session_state.log_data)
            st.dataframe(log_df)
        else:
            st.info("No logs available yet.")
