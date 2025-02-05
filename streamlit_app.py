import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

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
        st.write("Admin Dashboard: View all user logs.")

        logs_df = pd.read_sql("SELECT * FROM logs ORDER BY timestamp DESC", conn)
        if not logs_df.empty:
            logs_df.drop(columns=["id"], inplace=True)
            logs_df.set_index("timestamp", inplace=True)
            st.dataframe(logs_df)

            # Option to download logs as CSV
            csv = logs_df.to_csv(index=True).encode("utf-8")
            st.download_button("Download All Logs as CSV", data=csv, file_name="all_logs.csv", mime="text/csv")
        else:
            st.info("No logs available yet.")

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.is_admin = False
            st.rerun()
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
            
            model_type = st.selectbox("Select Model Type:", ["Transformer", "CNN", "RNN", "ANN"])
            core_option = st.selectbox("Select Core Option:", ["CPU", "GPU", "HDFS"])

            if st.button("Run"):
                if uploaded_file is None:
                    st.error("Please upload a valid file before running.")
                else:
                    dataset_size = uploaded_file.size / (1024 * 1024)  # Convert to MB
                    dataset_name = uploaded_file.name

                    c.execute('''INSERT INTO logs (username, dataset_name, dataset_size, model, cpu, gpu, hdfs, timestamp) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                              (st.session_state.username, dataset_name, f"{dataset_size:.2f} MB", model_type,
                               "Used" if core_option == "CPU" else "Not Used",
                               "Used" if core_option == "GPU" else "Not Used",
                               "Used" if core_option == "HDFS" else "Not Used",
                               datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    st.success("Run executed and details logged successfully!")

                    # Display model features dynamically based on selection
                    model_features = {
                        "Transformer": ["Epoch", "Batch Size", "Iteration", "Learning Rate", "Attention Mechanism"],
                        "CNN": ["Epoch", "Batch Size", "Iteration", "Learning Rate", "Convolutional Layers"],
                        "RNN": ["Epoch", "Batch Size", "Iteration", "Learning Rate", "Hidden States"],
                        "ANN": ["Epoch", "Batch Size", "Iteration", "Learning Rate", "Activation Functions"]
                    }

                    if model_type in model_features:
                        st.write("### Model Features")
                        for feature in model_features[model_type]:
                            st.write(f"- {feature}")

        elif page == "Log Page":
            st.title("Log Page")
            logs_df = pd.read_sql("SELECT * FROM logs ORDER BY timestamp DESC", conn)
            if not logs_df.empty:
                logs_df.drop(columns=["id"], inplace=True)
                logs_df.set_index("timestamp", inplace=True)
                st.dataframe(logs_df)

                # Option to download logs as CSV
                csv = logs_df.to_csv(index=True).encode("utf-8")
                st.download_button("Download Log as CSV", data=csv, file_name="log_data.csv", mime="text/csv")
            else:
                st.info("No logs available yet.")

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.is_admin = False
            st.rerun()

