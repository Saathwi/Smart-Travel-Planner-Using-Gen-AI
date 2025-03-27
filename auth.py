import json
import bcrypt

# File where user data is stored
USER_FILE = "users.json"


def load_users():
    """Load users from the JSON file."""
    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"users": []}


def save_users(users):
    """Save users to the JSON file."""
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)


def hash_password(password):
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password, hashed):
    """Check if the password matches the stored hashed password."""
    return bcrypt.checkpw(password.encode(), hashed.encode())


def register_user(username, password):
    """Register a new user."""
    users = load_users()

    # Check if username already exists
    for user in users["users"]:
        if user["username"] == username:
            return False, "Username already exists!"

    # Hash the password and save the user
    hashed_pwd = hash_password(password)
    users["users"].append({"username": username, "password": hashed_pwd})
    save_users(users)
    return True, "User registered successfully!"


def authenticate_user(username, password):
    """Authenticate a user."""
    users = load_users()

    for user in users["users"]:
        if user["username"] == username and check_password(password, user["password"]):
            return True
    return False
