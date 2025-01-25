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
                st.error("Please upload a valid file before running.")
            else:
                dataset_size = uploaded_file.size  # Get size of the uploaded file in bytes
                dataset_name = uploaded_file.name

                try:
                    # Read and display dataset columns
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                        st.write("### Columns in the Dataset")
                        st.write(list(df.columns))
                    else:
                        st.error("Unsupported file type. Please upload a CSV file.")

                    # Display dataset details
                    st.write(f"**Dataset Name:** {dataset_name}")
                    st.write(f"**Dataset Size:** {dataset_size / (1024 * 1024):.2f} MB")

                    # Display core option
                    st.write("### Core Used")
                    st.write(core_option)

                    # Display model type and features
                    st.write("### Model Type")
                    st.write(model_type)

                    # Display model features based on selection
                    features = {
                        "Transformer": ["Epoch", "Batch Size", "Iteration", "Learning Rate", "Attention Mechanism"],
                        "CNN": ["Epoch", "Batch Size", "Iteration", "Learning Rate", "Convolutional Layers"],
                        "RNN": ["Epoch", "Batch Size", "Iteration", "Learning Rate", "Hidden States"],
                        "ANN": ["Epoch", "Batch Size", "Iteration", "Learning Rate", "Activation Functions"]
                    }
                    
                    for feature in features[model_type]:
                        st.write(f"- {feature}")

                    # Log details into session state
                    new_log = {
                        "Dataset Name": dataset_name,
                        "Dataset Size": f"{dataset_size / (1024 * 1024):.2f} MB",
                        "Model": model_type,
                        "CPU": "Used" if core_option == "CPU" else "Not Used",
                        "GPU": "Used" if core_option == "GPU" else "Not Used",
                        "HDFS": "Used" if core_option == "HDFS" else "Not Used",
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.log_data.insert(0, new_log)  # Insert at the start for recent-first ordering

                    st.success("Run executed and details logged successfully!")

                except Exception as e:
                    st.error(f"Error processing the uploaded file: {e}")

    elif page == "Log Page":
        st.title("Log Page")
        st.write("This page logs all the model and dataset information during the session.")

        # Display Log Table
        if st.session_state.log_data:
            st.write("### Log Table")
            log_df = pd.DataFrame(st.session_state.log_data)
            st.dataframe(log_df)

            # Option to download the log data as CSV
            csv = log_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Log as CSV",
                data=csv,
                file_name='log_data.csv',
                mime='text/csv',
                key='download-csv'
            )
        else:
            st.info("No logs available yet.")
