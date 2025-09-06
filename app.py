from flask import Flask, render_template, request, jsonify,url_for
import os
import datetime
app = Flask(__name__)

USER_DATA_FILE = "users.txt"
# Function to check if user data file exists
if not os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, "w") as f:
        pass  # Create an empty file if it doesn't exist



def log_ride(start, destination, vehicle, cost_details):
    """Logs ride search details into a text file."""
    with open(LOG_FILE, "a") as file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Start: {start}, Destination: {destination}, Vehicle: {vehicle}, Costs: {cost_details}\n"
        file.write(log_entry)

@app.route("/log_ride", methods=["POST"])
def log_ride_endpoint():
    """API to log ride details."""
    data = request.json
    if not all(key in data for key in ["start", "destination", "vehicle", "costs"]):
        return jsonify({"error": "Missing data"}), 400
    
    log_ride(data["start"], data["destination"], data["vehicle"], data["costs"])
    return jsonify({"message": "Ride logged successfully"})

@app.route("/get_history", methods=["GET"])
def get_history():
    """API to fetch ride history."""
    try:
        with open(LOG_FILE, "r") as file:
            history = file.readlines()
        return jsonify({"history": history})
    except FileNotFoundError:
        return jsonify({"history": []})

@app.route("/history")
def history_page():
    """Render history page."""
    return render_template("history.html")


LOG_FILE = "ride_history"

# Home Route (Serves Sign In / Sign Up Page)
@app.route("/")
def home():
    global LOG_FILE
    LOG_FILE = "ride_history"
    return render_template("login.html")


# Sign Up Route
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    fullname, email, phone, password = data["fullname"], data["email"], data["phone"], data["password"]

    # Check if user already exists
    with open(USER_DATA_FILE, "r") as f:
        for line in f:
            stored_email, _ = line.strip().split(",", 1)
            if stored_email == email:
                return jsonify({"message": "User already exists! Try signing in."})

    # Store user data
    with open(USER_DATA_FILE, "a") as f:
        f.write(f"{email},{password},{fullname},{phone}\n")

    return jsonify({"message": "Sign Up Successful! Please Sign In."})

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")


# Sign In Route
@app.route("/signin", methods=["POST"])
def signin():
    data = request.json
    email, password = data["email"], data["password"]

    with open(USER_DATA_FILE, "r") as f:
        for line in f:
            stored_email, stored_password, _, _ = line.strip().split(",", 3)
            if stored_email == email and stored_password == password:
                global LOG_FILE
                LOG_FILE+=email+".txt"
                return jsonify({"redirect": url_for("dashboard")})

    return jsonify({"message": "Invalid Email or Password"})

@app.route("/check")
def check():
    return render_template("vehicle_cost.html")

@app.route("/act")
def act():
    return render_template("history.html")

if __name__ == "__main__":
    app.run(debug=True)
