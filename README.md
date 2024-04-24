# COP4521-Project

# Project Setup Instructions

## Initial Setup

1. **Install MongoDB:**
   Open your terminal and run these commands to install MongoDB on macOS:
   ```bash
   brew tap mongodb/brew
   brew install mongodb-community
   brew services start mongodb/brew/mongodb-community
   ```

## Configuration Steps

2. **Setup Python Environment:**
   In the project root directory create a venv and install the necessary Python packages:

   - Install Flask:
     ```bash
     pip install flask
     ```
   
   - Install PyMongo:
     ```bash
     pip3 install pymongo
     ```

   - Install yFinance:
     ```bash
     pip3 install yfinance
     ```
   - Install matplotlib:
     ```bash
     pip3 install matplotlib
     ```
   - Install PyMuPDF:
     ```bash
     pip install pymupdf
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
   - Once `mongosh` is running, connect to our database:
     ```bash
     use("userDatabase")
     ```
   - Example usage to view registered users:
     ```bash
     db.users.find({}, { password: 0, _id: 0 })
     ```

## Note

- A `.gitignore` file has been created to ensure that `venv` and other  files are not tracked by our git pushes.

change
