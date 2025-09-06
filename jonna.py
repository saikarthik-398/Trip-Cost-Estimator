import streamlit as st
import os
import datetime
import streamlit.components.v1 as components

USER_DATA_FILE = "users.txt"
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def get_log_file(email):
    return os.path.join(LOG_DIR, f"ride_history_{email}.txt")

def log_ride(email, start, destination, vehicle, cost_details):
    log_file = get_log_file(email)
    with open(log_file, "a") as file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Start: {start}, Destination: {destination}, Vehicle: {vehicle}, Costs: {cost_details}\n"
        file.write(log_entry)

def get_history(email):
    log_file = get_log_file(email)
    if os.path.exists(log_file):
        with open(log_file, "r") as file:
            return file.readlines()
    return []

def authenticate(email, password):
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            for line in f:
                stored_email, stored_password, _, _ = line.strip().split(",", 3)
                if stored_email == email and stored_password == password:
                    return True
    return False

def register_user(fullname, email, phone, password):
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            for line in f:
                stored_email, _ = line.strip().split(",", 1)
                if stored_email == email:
                    return False
    with open(USER_DATA_FILE, "a") as f:
        f.write(f"{email},{password},{fullname},{phone}\n")
    return True

# Load HTML file dynamically
def load_html(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# Authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.email = ""

# Display HTML Login Page
if not st.session_state.authenticated:
    login_html = load_html("templates/login.html")
    components.html(login_html, height=600, scrolling=True)

    option = st.radio("Select an option", ["Sign In", "Sign Up"])
    
    if option == "Sign In":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Sign In"):
            if authenticate(email, password):
                st.session_state.authenticated = True
                st.session_state.email = email
                st.success("Sign In Successful!")
                st.experimental_rerun()
            else:
                st.error("Invalid Email or Password")
    else:
        fullname = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        password = st.text_input("Password", type="password")
        if st.button("Sign Up"):
            if register_user(fullname, email, phone, password):
                st.success("Sign Up Successful! Please Sign In.")
            else:
                st.error("User already exists! Try signing in.")

# If authenticated, show dashboard
else:
    st.sidebar.write(f"Logged in as: {st.session_state.email}")
    if st.sidebar.button("Sign Out"):
        st.session_state.authenticated = False
        st.experimental_rerun()

    # Render Dashboard HTML
    dashboard_html = load_html("templates/index.html")
    components.html(dashboard_html, height=800, scrolling=True)

    st.header("Log a New Ride")
    start = st.text_input("Start Location")
    destination = st.text_input("Destination")
    vehicle = st.selectbox("Vehicle Type", ["Car", "Bike", "Bus", "Train"])
    cost = st.number_input("Cost", min_value=0.0, format="%.2f")
    
    if st.button("Log Ride"):
        log_ride(st.session_state.email, start, destination, vehicle, cost)
        st.success("Ride logged successfully!")

    st.header("Ride History")
    history = get_history(st.session_state.email)
    if history:
        for entry in history:
            st.text(entry.strip())
    else:
        st.info("No ride history available.")
