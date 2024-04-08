import sqlite3
from PasswordHashing import hash_password

def create_connection(db_file):
    """Create a database connection to the SQLite database."""
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return None

def create_table(conn):
    """Create a table for the users"""
    try:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                            username TEXT PRIMARY KEY,
                            password TEXT NOT NULL,
                            name TEXT NOT NULL,
                            date_of_birth TEXT NOT NULL
                        )""")
        print("Table 'users' created successfully.")
    except sqlite3.Error as e:
        print("Error creating table:", e)


def registerUser(conn, username, password, name, date_of_birth):
    """Register a new user."""
    hashed_password = hash_password(password)
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, name, date_of_birth) VALUES (?, ?, ?, ?)",
                       (username, hashed_password, name, date_of_birth))
        conn.commit()
        print(f"User {username} registered successfully!")
    except sqlite3.IntegrityError:
        print("Username already exists. Try a different one.")

def login(conn, username, hashed_password):
    """Log in an existing user."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
        user = cursor.fetchone()
        if user:
            print(f"Welcome back {user[2]}!") 
            return True, user
        else:
            print("Invalid username or password")
            return False, None
    except sqlite3.Error as e:
        print(e)
        return False, None