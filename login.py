# login.py
import streamlit as st
import streamlit_authenticator as stauth
from pathlib import Path
import pickle

# Load hashed passwords (you need to create this file with hashed passwords)
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)
# Define users
names = ["User1", "User2"]
usernames = ["user1", "user2"]

# Create authenticator object
authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    "some_cookie_name", "some_signature_key", cookie_expiry_days=30)

# Display login form
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.success(f"Welcome {name}!")
    # Redirect to main app after successful login
    import main_app  # Assuming your main app is in main_app.py
    main_app.run()
elif authentication_status is False:
    st.error("Username/password is incorrect")
else:
    st.warning("Please enter your username and password")
