import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import openai
import nbformat
import os
from nbconvert.preprocessors import ExecutePreprocessor
from datetime import datetime

# Set OpenAI API Key (Replace this with your actual key)
openai.api_key = "YOUR_OPENAI_API_KEY"

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
    generated_code TEXT,
    execution_status TEXT,
    timestamp TEXT
)''')
conn.commit()

# Ensure `notebooks/` directory exists
if not os.path.exists("notebooks"):
    os.makedirs("notebooks")

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

# ✅ Updated Function to Generate Python Code Using OpenAI API (Fixed)
def generate_python_code(prompt):
    response = openai.chat.completions.create(  # ✅ Updated OpenAI API call
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert Python programmer."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content  # ✅ Fixed attribute access

# Function to create a Jupyter notebook from generated code
def create_notebook(username, generated_code):
    notebook_name = f"notebooks/{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ipynb"
    
    # Create a new notebook
    nb = nbformat.v4.new_notebook()
    code_cell = nbformat.v4.new_code_cell(generated_code)
    nb.cells.append(code_cell)

    # Save notebook
    with open(notebook_name, 'w') as f:
        nbformat.write(nb, f)
    
    return notebook_name

# Function to execute the generated notebook
def execute_notebook(notebook_path):
    try:
        with open(notebook_path) as f:
            nb = nbformat.read(f, as_version=4)
        
        executor = ExecutePreprocessor(timeout=600, kernel_name='python3')
        executor.preprocess(nb)

        with open(notebook_path, 'w') as f:
            nbformat.write(nb, f)

        return "Execution Successful"
    except Exception as e:
        return f"Execution Failed: {str(e)}"

# Register default users
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

# Initialize session states
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.is_admin = False

# Login Page
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
        logs_df = pd.read_sql(
            "SELECT username, dataset_name, dataset_size, model, cpu, gpu, hdfs, generated_code, execution_status, timestamp FROM logs ORDER BY timestamp DESC",
            conn
        )
        if not logs_df.empty:
            logs_df.set_index("timestamp", inplace=True)
            st.dataframe(logs_df)
    else:
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Go to", ["Dashboard", "Log Page"])

        if page == "Dashboard":
            st.title("Dataset Uploader and Model Selector")

            # Upload Dataset
            uploaded_file = st.file_uploader("Upload your dataset (CSV)", type=["csv"])

            if uploaded_file is not None:
                dataset = pd.read_csv(uploaded_file)
                st.write("### Dataset Preview")
                st.dataframe(dataset.head())

            # Select Model Type
            model_type = st.selectbox("Select Model Type:", ["Transformer", "CNN", "RNN", "ANN"])
            
            # Select Core Option
            core_option = st.selectbox("Select Core Option:", ["CPU", "GPU", "HDFS"])

            # Generate Python Code
            prompt = st.text_area("Describe your Python task (e.g., 'Train a Transformer model on the dataset')")
            generated_code = ""

            if st.button("Generate Code"):
                if prompt:
                    generated_code = generate_python_code(prompt)
                    st.code(generated_code, language="python")
                else:
                    st.error("Please enter a prompt to generate code.")

            # Execute Code in Jupyter Notebook
            if generated_code:
                if st.button("Execute Code in Notebook"):
                    notebook_path = create_notebook(st.session_state.username, generated_code)
                    execution_status = execute_notebook(notebook_path)

                    # Log execution
                    c.execute('''INSERT INTO logs (username, dataset_name, dataset_size, model, cpu, gpu, hdfs, generated_code, execution_status, timestamp) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                              (st.session_state.username, uploaded_file.name if uploaded_file else "No Dataset",
                               f"{uploaded_file.size / (1024 * 1024):.2f} MB" if uploaded_file else "0 MB",
                               model_type,
                               "Used" if core_option == "CPU" else "Not Used",
                               "Used" if core_option == "GPU" else "Not Used",
                               "Used" if core_option == "HDFS" else "Not Used",
                               generated_code, execution_status,
                               datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    st.success(f"Notebook executed successfully. Status: {execution_status}")

        elif page == "Log Page":
            st.title("Log Page")
            logs_df = pd.read_sql(
                "SELECT dataset_name, dataset_size, model, cpu, gpu, hdfs, generated_code, execution_status, timestamp FROM logs WHERE username = ? ORDER BY timestamp DESC",
                conn, params=(st.session_state.username,))
            if not logs_df.empty:
                logs_df.set_index("timestamp", inplace=True)
                st.dataframe(logs_df)

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.is_admin = False
            st.rerun()
