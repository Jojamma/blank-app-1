import streamlit as st
import pandas as pd
from datetime import datetime

# Hardcoded credentials for demonstration (use a secure method in production)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "jogu@2003"
USER_USERNAME = "user"
USER_PASSWORD = "user@123"

# Function to check credentials
def check_credentials(username, password):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return True, True  # Admin login
    elif username == USER_USERNAME and password == USER_PASSWORD:
        return True, False  # User login
    return False, None  # Invalid login

# Initialize session states if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

if 'log_data' not in st.session_state:
    st.session_state.log_data = []

if 'user_logs' not in st.session_state:
    st.session_state.user_logs = []

# Login page logic
if not st.session_state.logged_in:
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        valid, is_admin = check_credentials(username, password)
        if valid:
            st.session_state.logged_in = True
            st.session_state.is_admin = is_admin  # Set user role based on login
            st.query_params = {"logged_in": "true"}
        else:
            st.error("Invalid username or password.")
else:
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    if st.session_state.is_admin:
        page = st.sidebar.radio("Go to", ["Admin Dashboard", "Log Page"])
    else:
        page = st.sidebar.radio("Go to", ["Dashboard", "Log Page"])

    if page == "Admin Dashboard" and st.session_state.is_admin:
        st.title("Admin Dashboard")

        # Display all user logs
        if st.session_state.user_logs:
            log_df = pd.DataFrame(st.session_state.user_logs)
            st.write("### User Logs")
            st.dataframe(log_df)

            # Option to download user logs as CSV
            csv = log_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download User Logs as CSV",
                data=csv,
                file_name='user_logs.csv',
                mime='text/csv',
                key='download-user-logs'
            )
        else:
            st.info("No user logs available yet.")

    elif page == "Dashboard" and not st.session_state.is_admin:
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
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "User": username  # Log the username of the user running this action.
                    }
                    
                    # Insert logs into respective session states
                    st.session_state.log_data.insert(0, new_log)
                    st.session_state.user_logs.insert(0, new_log)  # Log for admin monitoring

                    st.success("Run executed and details logged successfully!")

                except Exception as e:
                    st.error(f"Error processing the uploaded file: {e}")

    elif page == "Log Page":
        st.title("Log Page")

        # Display Log Table
        if st.session_state.log_data:
            log_df = pd.DataFrame(st.session_state.log_data)
            st.write("### Log Table")
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

        # Disclaimer about log data at the bottom of the page
        st.warning("**Disclaimer:** The log results will not be saved once you log out. Please download the log data if you wish to keep a record.")
