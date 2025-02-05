import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime
import time
import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import openai

# Set the OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"  # Replace with your actual API key

# Database initialization
conn = sqlite3.connect("user_data.db", check_same_thread=False)
c = conn.cursor()

# Create tables if they don’t exist
c.execute('''CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password_hash TEXT,
    is_admin INTEGER
)''')
c.execute('''CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    dataset_name TEXT,
    dataset_size TEXT,
    model TEXT,
    cpu TEXT,
    gpu TEXT,
    hdfs TEXT,
    user_code TEXT DEFAULT 'No Code Provided',
    notebook_path TEXT DEFAULT '',
    timestamp TEXT
)''')
conn.commit()

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to check credentials
def check_credentials(username, password):
    c.execute("SELECT password_hash, is_admin FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    if user and user[0] == hash_password(password):
        return True, bool(user[1])
    return False, False

# Function to register default users
def register_default_users():
    default_users = {
        "admin": ("admin@123", 1),
        "user1": ("user@123", 0),
        "user2": ("user2@123", 0),
        "user3": ("user3@123", 0)
    }
    for user, (pwd, is_admin) in default_users.items():
        c.execute("INSERT OR IGNORE INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                  (user, hash_password(pwd), is_admin))
    conn.commit()

register_default_users()  # Run once to register default users

# Function to generate Python code dynamically using OpenAI (Fixed for API v1.0.0+)
def generate_code(dataset_path, model, mode):
    """Generates Python code for the given dataset, model, and execution mode."""
    prompt = f"""
    Generate Python code to train a {model} model on a dataset located at {dataset_path}.
    Use {mode} mode for execution. Include comments and timestamps for each step.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Python expert specializing in machine learning."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7  # Adjust temperature for creativity level
        )
        return response.choices[0].message.content  # Fixed OpenAI API syntax
    
    except Exception as e:
        return f"# Error generating code: {e}"

# Function to execute the generated code in a Jupyter Notebook
def execute_jupyter_notebook(generated_code):
    """Executes the generated Python code in a Jupyter Notebook."""
    timestamp = int(time.time())
    notebook_path = f"notebooks/generated_notebook_{timestamp}.ipynb"

    # Create a new Jupyter notebook
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell(generated_code))

    # Ensure the `notebooks/` directory exists
    os.makedirs("notebooks", exist_ok=True)
    with open(notebook_path, "w") as f:
        nbformat.write(nb, f)

    # Execute the notebook
    try:
        ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
        with open(notebook_path, "r") as f:
            nb = nbformat.read(f, as_version=4)
        ep.preprocess(nb, {"metadata": {"path": "./"}})

        with open(notebook_path, "w") as f:
            nbformat.write(nb, f)

        return notebook_path
    except Exception as e:
        return f"Execution failed: {e}"

# Initialize session states
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.is_admin = False

# Login page logic
if not st.session_state.logged_in:
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        valid, is_admin = check_credentials(username, password)
        if valid:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.is_admin = is_admin
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.error("Invalid username or password.")
else:
    if st.session_state.is_admin:
        st.title("Admin Dashboard")
        try:
            logs_df = pd.read_sql(
                "SELECT username, dataset_name, dataset_size, model, cpu, gpu, hdfs, user_code, notebook_path, timestamp FROM logs ORDER BY timestamp DESC",
                conn
            )
            if not logs_df.empty:
                logs_df.set_index("timestamp", inplace=True)
                st.dataframe(logs_df)
        except Exception as e:
            st.error(f"Error loading logs: {e}")
    else:
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Go to", ["Dashboard", "Log Page"])

        if page == "Dashboard":
            st.title("Dataset Uploader and Model Selector")
            uploaded_file = st.file_uploader("Upload your dataset (CSV)", type=["csv"])

            if uploaded_file is not None:
                dataset = pd.read_csv(uploaded_file)
                st.write("### Dataset Columns")
                st.write(dataset.columns.tolist())

            # Code Generation and Execution
            model_type = st.selectbox("Select Model Type:", ["Transformer", "CNN", "RNN", "ANN"])
            core_option = st.selectbox("Select Core Option:", ["CPU", "GPU", "HDFS"])
            generate_code_button = st.button("Generate Code")

            if generate_code_button and uploaded_file is not None:
                dataset_path = uploaded_file.name
                generated_code = generate_code(dataset_path, model_type, core_option)
                st.session_state["generated_code"] = generated_code
                st.code(generated_code, language="python")

            execute_button = st.button("Execute Code")

            if execute_button and "generated_code" in st.session_state:
                notebook_path = execute_jupyter_notebook(st.session_state["generated_code"])
                st.success(f"Notebook executed successfully! [Download Notebook]({notebook_path})")

        elif page == "Log Page":
            st.title("Log Page")
            logs_df = pd.read_sql(
                "SELECT dataset_name, dataset_size, model, cpu, gpu, hdfs, user_code, notebook_path, timestamp FROM logs WHERE username = ? ORDER BY timestamp DESC",
                conn, params=(st.session_state.username,))
            if not logs_df.empty:
                logs_df.set_index("timestamp", inplace=True)
                st.dataframe(logs_df)

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.is_admin = False
            st.rerun()
