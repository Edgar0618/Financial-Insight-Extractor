from flask import Flask, render_template, request, redirect, url_for
from Database import create_connection, create_table, registerUser, login
from PasswordHashing import hash_password

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        conn = create_connection('db_file.db')
        if conn is not None:
            create_table(conn)
            username = request.form['username']
            password = request.form['password']
            name = request.form['name']
            date_of_birth = request.form['date_of_birth'] 
            registerUser(conn, username, password, name, date_of_birth)
            conn.close()
            return redirect(url_for('index')) # redirects after registration
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    error = None
    if request.method == 'POST':
        conn = create_connection('db_file.db')
        if conn is not None:
            username = request.form['username']
            password = request.form['password']
            hashed_password = hash_password(password)
            success, user = login(conn, username, hashed_password)
            if success:
                # Redirect to instructions after successful login
                return redirect(url_for('instructions'))
            else:
                error = "Invalid username or password"
    return render_template('login.html', error=error)

@app.route('/instructions')
def instructions():
    return render_template('instructions.html')

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if'pdf_file' not in request.files:
        return "No file part"

    pdf_file = request.files['pdf_file']
    if pdf_file.filename == '':
        return "No selected file"

    return "File uploaded"

if __name__ == '__main__':
    app.run(debug=True)
