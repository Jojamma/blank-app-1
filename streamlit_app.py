import streamlit as st
import pandas as pd

# Hardcoded credentials for demonstration (use a secure method in production)
USERNAME = "admin"
PASSWORD = "password"

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
            st.success("Logged in successfully!")
            # Use st.rerun() to refresh the app state
            st.rerun()
        else:
            st.error("Invalid username or password.")
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

        # Display selected model type and core option only after Run button is clicked and file is uploaded
        if uploaded_file and run_button_clicked:
            st.write(f"Model Type: {model_type}")
            st.write(f"Core Option: {core_option}")

            # New button at the end of the output section that opens a new tab
            if st.button("Open New Page"):
                # Create an HTML link that opens in a new tab
                new_page_url = "https://example.com"  # Replace with your desired URL or page path
                st.markdown(f'<a href="{new_page_url}" target="_blank">Go to New Page</a>', unsafe_allow_html=True)
