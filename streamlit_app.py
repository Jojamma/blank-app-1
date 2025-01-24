import streamlit as st

# Title of the app
st.title("Model Runner")

# Input for dataset path
dataset_path = st.text_input("Dataset Path:")

# Dropdown for model type selection
model_type = st.selectbox("Select Model Type:", ["Transformer", "CNN", "RNN"])

# Dropdown for core options selection
core_option = st.selectbox("Select Core Option:", ["CPU", "GPU", "HDFS"])

# Button to run the model
if st.button("Run"):
    # Here you would add the logic to run your model based on the inputs
    # For demonstration purposes, we just display the inputs
    st.write(f"Dataset Path: {dataset_path}")
    st.write(f"Model Type: {model_type}")
    st.write(f"Core Option: {core_option}")
    
    # Add your model running logic here
    # For example:
    # result = run_model(dataset_path, model_type, core_option)
    # st.write(f"Model Output: {result}")

