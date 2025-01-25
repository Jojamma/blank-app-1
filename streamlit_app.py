# Outputs displayed at the bottom
if run_button_clicked:
    if uploaded_file is None:
        st.error("Please upload a valid file before running.")
    else:
        dataset_size = uploaded_file.size  # Get size of the uploaded file in bytes

        try:
            # Display column names for CSV files
            if uploaded_file.name.endswith('.csv'):
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
            st.error(f"Error processing the uploaded file: {e}")
