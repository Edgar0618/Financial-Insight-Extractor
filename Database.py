from pymongo import MongoClient, errors
from PasswordHashing import hash_password

def createConnection():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.userDatabase
    return db

def createCollection(db):
    if "users" not in db.list_collection_names():
        db.create_collection("users")
        db.users.create_index("username", unique=True)
        print("Collection 'users' created successfully.")
    else:
        print("Collection 'users' already exists.")

def registerUser(db, username, password, name, date_of_birth, is_admin=False):
    hashed_password = hash_password(password)
    try:
        db.users.insert_one({
            "username": username,
            "password": hashed_password,
            "name": name,
            "date_of_birth": date_of_birth,
            "is_admin": is_admin
        })
        return True, f"User {username} registered successfully!"
    except errors.DuplicateKeyError:
        return False, "Username already exists. Try a different one."

def login(db, username, hashed_password):
    user = db.users.find_one({"username": username, "password": hashed_password})
    if user:
        print(f"Welcome back {user['name']}!")
        return True, user
    else:
        print("Invalid username or password")
        return False, None
