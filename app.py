from flask import Flask, render_template, request, redirect, url_for, session
from Database import createConnection, createCollection, registerUser, login
from PasswordHashing import hash_password, verify_password
import yfinance as yf

app = Flask(__name__)
app.secret_key = '1'

sector_companies = {
    "Financial": ["AGBA", "SQQQ", "TQQQ", "SPY", "MARA"],
    "Tech": ["MTTR", "NVDA", "AMD", "AAPL", "INTC"],
    "Communication_services": ["T", "VZ", "AMC", "GOOGL", "SNAP"],
    "Healthcare": ["JAGX", "NIVF", "MLEC", "DNA", "SINT"],
    "Energy": ["PBR", "TEL", "RIG", "KMI", "XOM"],
    "Utilities": ["NEE", "PCG", "AES", "SO", "EXC"],
    "Consumer_Cyclical": ["TSLA", "F", "NIO", "FFIE", "AMZN"],
    "Industrials": ["SPCB", "NKLA", "FCEL", "SPCE", "AAL"],
    "Real_Estate": ["AGNC", "MPW", "VICI", "OPEN", "BEKE"],
    "Basic_Materials": ["VALE", "GOLD", "KGC", "FCX", "BTG"],
    "Consumer_Defensive": ["KVUE", "EDBL", "KO", "WMT", "ABEV"]
}


@app.route('/')
def index():
    if 'username' in session:
        db = createConnection()
        user = db.users.find_one({"username": session['username']})
        if user:
            return render_template('index.html', name=user['name'], is_logged_in=True)
        else:
            return "User not found!", 404
    return render_template('index.html', name="Guest", is_logged_in=False)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('instructions'))

    if request.method == 'POST':
        db = createConnection()
        createCollection(db)
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        date_of_birth = request.form['date_of_birth']
        registerUser(db, username, password, name, date_of_birth)
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if 'username' in session:
        return redirect(url_for('index'))
    error = None
    if request.method == 'POST':
        db = createConnection()
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)
        success, user = login(db, username, hashed_password)
        if success:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            error = "Invalid username or password"

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/instructions', methods=['GET'])
def instructions():
    if 'username' in session:
        db = createConnection()
        user = db.users.find_one({"username": session['username']})
        return render_template('instructions.html', name=user['name'])
    return render_template('instructions.html')


@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'username' not in session:
        return redirect(url_for('login'))
    if 'pdf_file' not in request.files:
        return "No file part"
    pdf_file = request.files['pdf_file']
    if pdf_file.filename == '':
        return "No selected file"
    return "File uploaded"


@app.route('/compare', methods=['GET', 'POST'])
def compare():
    msft = yf.Ticker("MSFT")
    print(msft.info)
    sector = request.form.get('sectors')
    option = request.form.get('options')
    results = []
    average = []
    if sector in sector_companies:
        for symbol in sector_companies[sector]:
            ticker = yf.Ticker(symbol)
            try:
                if option == 'net_income':
                    income_statement = ticker.financials
                    result = income_statement.loc['Net Income'].iloc[0]
                    # value = [symbol] + ": " + ticker + ":" + income_statement.loc['Net Income'][0]

                elif option == 'revenue':
                    revenue_statement = ticker.financials
                    result = revenue_statement.loc['Total Revenue'].iloc[0]

                elif option == 'earnings_per_share':
                    info = ticker.info
                    if 'revenuePerShare' in info:
                        result = info['revenuePerShare']
                    else:
                        print("No revenue per share data for", symbol)

                elif option == 'operating_income':
                    income_statement = ticker.financials
                    result = income_statement.loc['Operating Income'].iloc[0]
                else:
                    continue

                # list.append(value)
                results.append((symbol, result))
                average.append(result)
            except Exception as e:
                print("Error getting datra for symbl {symbol}: {e}")

        results.sort(key=lambda x: x[1], reverse=True)

        display = ", ".join([f"{symbol}: {value:,.2f}" for symbol, value in results])
        # result_txt = f""

        if results:
            avg_result = sum(average) / len(average)
            result_txt = f"Vals for {option} in {sector}: {display} \n Avg: {option} for {sector}: ${avg_result:,.2f}"
        else:
            result_txt = "Wont work spongebob"

        return render_template('compare.html', result=result_txt)

    return render_template('compare.html')

    # sectors:Financial, Tech, Communication services, Healthcare,Energy, Utilities,
    # Consumer Cyclical, Industrials, Real Estate, Basic Materials, Financials

@app.route('/profile')
def profile():
    if 'username' in session:
        db = createConnection()
        user = db.users.find_one({"username": session['username']})
        if user:
            return render_template('profile.html', name=user['name'], username=user['username'])
        else:
            return "User not found!", 404
    return render_template('compare.html')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        return redirect(url_for('login_page'))

    message = ""  # Variable to store message to the user
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        db = createConnection()
        user = db.users.find_one({"username": session['username']})

        if user and verify_password(user['password'], current_password):
            hashed_new_password = hash_password(new_password)
            # Update the password in the database
            db.users.update_one({"username": session['username']}, {"$set": {"password": hashed_new_password}})
            message = 'Password successfully changed.'
            return redirect(url_for('profile'))  # Redirect to profile with a success message or you could pass message through query parameter
        else:
            message = 'Current password is incorrect.'

    return render_template('change_password.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)