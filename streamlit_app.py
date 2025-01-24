# main_app.py
import streamlit as st

def run():
    # Title of the app
    st.title("Large File Uploader")

    # File uploader for dataset
    uploaded_file = st.file_uploader("Upload your dataset (supports large files up to 50GB)", type=None)

    # Dropdown for model type selection
    model_type = st.selectbox("Select Model Type:", ["Transformer", "CNN", "RNN"])

    # Dropdown for core options selection
    core_option = st.selectbox("Select Core Option:", ["CPU", "GPU", "HDFS"])

    # Button to process the uploaded file
    if st.button("Run"):
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                try:
                    st.write("Processing CSV file...")
                    chunk_size = 10 ** 6  # Adjust chunk size as needed
                    
                    for chunk in pd.read_csv(uploaded_file, chunksize=chunk_size):
                        st.write(f"Processed a chunk with {len(chunk)} rows.")
                    
                    st.write("CSV processing complete.")
                except Exception as e:
                    st.error(f"Error reading CSV file: {e}")
            else:
                st.write("File uploaded successfully but not recognized as a CSV.")

        else:
            st.error("Please upload a valid file.")

        # Display selected model type and core option
        st.write(f"Model Type: {model_type}")
        st.write(f"Core Option: {core_option}")

if __name__ == "__main__":
    run()
