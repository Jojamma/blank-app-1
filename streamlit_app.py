import streamlit as st
import pandas as pd

# Hardcoded credentials for demonstration (use a secure method in production)
USERNAME = "admin"
PASSWORD = "jogu@2003"

# Function to check credentials
def check_credentials(username, password):
    return username == USERNAME and password == PASSWORD

# Initialize session states if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Initialize dashboard stats
if 'uploaded_file_count' not in st.session_state:
    st.session_state.uploaded_file_count = 0

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

    # Create three columns for layout: Dashboard, Inputs, and Outputs
    dashboard_col, input_col, output_col = st.columns([1, 2, 2])

    # Dashboard in the left column
    with dashboard_col:
        st.subheader("Dashboard")
        st.metric("Total Uploaded Files", st.session_state.uploaded_file_count)
        st.metric("Last Core Used", st.session_state.get("last_core", "N/A"))
        st.metric("Last Model Type", st.session_state.get("last_model", "N/A"))

    # Inputs in the middle column
    with input_col:
        uploaded_file = st.file_uploader("Upload your dataset (supports large files up to 50GB)", type=["csv"])
        model_type = st.selectbox("Select Model Type:", ["Transformer", "CNN", "RNN", "ANN"])
        core_option = st.selectbox("Select Core Option:", ["CPU", "GPU", "HDFS"])
        run_button_clicked = st.button("Run")

    # Outputs in the right column
    if run_button_clicked:
        if uploaded_file is None:
            with output_col:
                st.error("Please upload a valid file before running.")
        else:
            # Update dashboard stats
            st.session_state.uploaded_file_count += 1
            st.session_state.last_core = core_option
            st.session_state.last_model = model_type

            try:
                with output_col:
                    # Display column names for CSV files
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                        st.write("### Columns in the Dataset")
                        st.write(list(df.columns))
                    else:
                        st.error("Unsupported file type. Please upload a CSV file.")

                    # Display core option
                    st.write("### Core Used")
                    st.write(core_option)

                    # Display model type
                    st.write("### Model Type")
                    st.write(model_type)

                    # Display features based on the selected model type
                    st.write("### Model Features")
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

            except Exception as e:
                with output_col:
                    st.error(f"Error processing the uploaded file: {e}")
