# COP4521-Project

# Project Setup Instructions

## Initial Setup

1. **Install MongoDB:**
   Open your terminal and run the following commands to install MongoDB on macOS:
   ```bash
   brew tap mongodb/brew
   brew install mongodb-community
   brew services start mongodb/brew/mongodb-community
   ```

## Configuration Steps

2. **Setup Python Environment:**
   In the project root directory, install the necessary Python packages:

   - Install Flask:
     ```bash
     pip install flask
     ```
   
   - Install PyMongo:
     ```bash
     pip3 install pymongo
     ```

## Optional Tools

3. **Install and Use MongoDB Shell (mongosh):**
   - To install `mongosh`, run:
     ```bash
     brew install mongosh
     ```
   - To start `mongosh`, simply type:
     ```bash
     mongosh
     ```
   - Once `mongosh` is running, connect to your project's database:
     ```bash
     use("userDatabase")
     ```
   - To view registered users without displaying their passwords or IDs, run:
     ```bash
     db.users.find({}, { password: 0, _id: 0 })
     ```

## Note

- A `.gitignore` file has been created to ensure that `venv` and other non-essential files are not tracked by Git. You do not need to delete `venv` every time you push changes to the repository.
