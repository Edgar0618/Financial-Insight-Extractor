from flask import Flask, render_template, request, redirect, url_for, session, render_template_string
from Database import createConnection, createCollection, registerUser, login, logScan
from PasswordHashing import hash_password, verify_password
import yfinance as yf
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor, as_completed
import io
import base64
import fitz  # PyMuPDF
import re

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

sample_earnings = {
    'last_year':[20000, 25000, 18000, 30000],
    'this_year':[0,0,0,0]
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
    error = None
    if request.method == 'POST':
        db = createConnection()
        createCollection(db)
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        date_of_birth = request.form['date_of_birth']
        admin_checked = 'admin' in request.form
        secret_key = request.form.get('secret_key', '')

        correct_secret_key = "admin"
        is_admin = admin_checked and secret_key == correct_secret_key

        success, message = registerUser(db, username, password, name, date_of_birth, is_admin)
        if success:
            return redirect(url_for('index'))
        else:
            error = message

    return render_template('register.html', error=error)

@app.route('/admindashboard')
def admin_dashboard():
    if 'username' in session:
        db = createConnection()
        user = db.users.find_one({"username": session['username']})
        if user and user.get('is_admin', False):
            users = db.users.find({})
            return render_template('admindashboard.html', users=users)
        else:
            return redirect(url_for('index'))
    return redirect(url_for('login_page'))


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if 'username' in session:
        # If user is already logged in, redirect to index
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
            if user.get('is_admin', False):
                return redirect(url_for('admin_dashboard'))
            else:
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

def extract_text_from_pdf(pdf_stream):
    with fitz.open(stream=pdf_stream.read(), filetype="pdf") as pdf:
        text = ""
        for page in pdf:
            text += page.get_text()
    return text

# Function to parse relevant data from text
def parse_financial_data(text):
    patterns = {
        'total_current_assets': r'Total current assets\s+(\d{1,3}(?:,\d{3})*)\s+(\d{1,3}(?:,\d{3})*)',
        'total_assets': r'Total assets\s+(\d{1,3}(?:,\d{3})*)\s+(\d{1,3}(?:,\d{3})*)',
        'total_current_liabilities': r'Total current liabilities\s+(\d{1,3}(?:,\d{3})*)\s+(\d{1,3}(?:,\d{3})*)',
        'total_stockholders_equity': r'Total stockholders’ equity\s+(\d{1,3}(?:,\d{3})*)\s+(\d{1,3}(?:,\d{3})*)',
        'total_liabilities_and_stockholders_equity': r'Total liabilities and stockholders’ equity\s+(\d{1,3}(?:,\d{3})*)\s+(\d{1,3}(?:,\d{3})*)',

        'cash_beginning': r'CASH, CASH EQUIVALENTS, AND RESTRICTED CASH, BEGINNING OF PERIOD\s+(\d{1,3}(?:,\d{3})*)\s+(\d{1,3}(?:,\d{3})*)',
        'net_income': r'Net income \(loss\)\s+(\d{1,3}(?:,\d{3})*)\s+(\d{1,3}(?:,\d{3})*)',
        'net_operating_cash': r'Net cash provided by \(used in\) operating activities\s+(\d{1,3}(?:,\d{3})*)\s+(\d{1,3}(?:,\d{3})*)',
        'net_investing_cash': r'Net cash used in investing activities\s+(\d{1,3}(?:,\d{3})*)\s+(\d{1,3}(?:,\d{3})*)',
        'net_financing_cash': r'Net cash provided by \(used in\) financing activities\s+(\d{1,3}(?:,\d{3})*)\s+(\d{1,3}(?:,\d{3})*)',
        'cash_end': r'CASH, CASH EQUIVALENTS, AND RESTRICTED CASH, END OF PERIOD\s+(\d{1,3}(?:,\d{3})*)\s+(\d{1,3}(?:,\d{3})*)',
        
        'total_net_sales': r'Total net sales\s+(\d{1,3}(?:,\d{3})*)\s+(\d{1,3}(?:,\d{3})*)',
        'total_operating_expenses': r'Total operating expenses\s+(\d{1,3}(?:,\d{3})*)\s+(\d{1,3}(?:,\d{3})*)',
        'net_income': r'Net income \(loss\)\s+(\d{1,3}(?:,\d{3})*)\s+(\d{1,3}(?:,\d{3})*)',
        'basic_earnings_per_share': r'Basic Earnings Per Share\s+(\-?\d+\.\d+)\s+(\-?\d+\.\d+)',
        'diluted_earnings_per_share': r'Diluted Earnings Per Share\s+(\-?\d+\.\d+)\s+(\-?\d+\.\d+)',
    }
    data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            data[key] = {
                '2022': match.group(1), 
                '2023': match.group(2)  
            }
        else:
            data[key] = {
                '2022': "Not found",
                '2023': "Not found"
            }
    return data

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'username' not in session:
        return redirect(url_for('login'))
    if 'pdf_file' not in request.files:
        return "No file part", 400
    pdf_file = request.files['pdf_file']
    if pdf_file and allowed_file(pdf_file.filename):
        text = extract_text_from_pdf(pdf_file.stream)
        data = parse_financial_data(text)

        market_tickers = {
            'S&P 500': '^GSPC',
            'Dow 30': '^DJI',
            'Nasdaq': '^IXIC',
            'Russell 2000': '^RUT',
            'Crude Oil': 'CL=F',
            'Gold': 'GC=F'
        }

        live_market_data = {}
        for name, ticker in market_tickers.items():
            individual_ticker_info = yf.Ticker(ticker).info
            live_market_data[name] = individual_ticker_info.get('regularMarketPrice') or individual_ticker_info.get('previousClose', 'N/A')

        tickerSymbol = 'MSFT'
        ticker_info = yf.Ticker(tickerSymbol).info

        other_ticker_data = {
            'ticker': tickerSymbol,
            'current_price': ticker_info.get('currentPrice', 'N/A'),
            'pe_ratio': ticker_info.get('trailingPE', 'N/A'),
            'week_change': ticker_info.get('52WeekChange', 'N/A'),
            'earnings_growth': ticker_info.get('earningsGrowth', 'N/A'),
        }

        db = createConnection()
        logScan(db, session['username'], pdf_file.filename)
        return render_template('scanResults.html', data=data, live_market_data=live_market_data, ticker_info=other_ticker_data)
    else:
        return "Invalid file or no file selected", 400

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@app.route('/compare', methods=['GET', 'POST'])
def compare():
    if request.method == 'POST':
        sector = request.form.get('sectors')
        option = request.form.get('options')
        results = []
        total = 0
        valid_data_count = 0  # To count entries with actual data for averaging

        if sector in sector_companies:
            for symbol in sector_companies[sector]:
                ticker = yf.Ticker(symbol)
                ticker.financials.index = ticker.financials.index.str.strip()  # Clean index names
                try:
                    data_point = None
                    # Check for the required financial metric based on user selection
                    if option == 'Net Income':
                        data_point = ticker.financials.loc['Net Income'].iloc[0] if ('Net Income'
                            in ticker.financials.index and ticker.financials.loc['Net Income'].iloc[0] != 0) else None
                    elif option == 'Revenue':
                        data_point = ticker.financials.loc['Total Revenue'].iloc[0] if ('Total Revenue'
                            in ticker.financials.index and ticker.financials.loc['Total Revenue'].iloc[0] != 0) else None
                    elif option == 'Earnings Per Share':
                        data_point = ticker.info.get('revenuePerShare', None)
                    elif option == 'Operating Income':
                        data_point = ticker.financials.loc['Operating Income'].iloc[0] if ('Operating Income'
                            in ticker.financials.index and ticker.financials.loc['Operating Income'].iloc[0] != 0) else None
                    elif option == 'Profit':
                        data_point = ticker.financials.loc['Gross Profit'].iloc[0] if ('Gross Profit'
                            in ticker.financials.index and ticker.financials.loc['Gross Profit'].iloc[0] != 0) else None

                    if data_point is None:
                        formatted_value = "Data Unavailable"
                    else:
                        formatted_value = "{:,.2f}".format(data_point)
                        total += data_point
                        valid_data_count += 1

                    results.append((symbol, formatted_value))  # Move this outside the else to include both cases

                except Exception as e:
                    print(f"Error getting data for {symbol}: {str(e)}")
                    results.append((symbol, "Data Unavailable"))

            if results:
                average = "{:,.2f}".format(total / valid_data_count) if valid_data_count else "Data Unavailable"
                return render_template('compare.html', results=results, average=average, sector=sector, option=option)
            else:
                return render_template('compare.html', message="No data available.")
        else:
            return render_template('compare.html', message="Invalid sector selected.")
    return render_template('compare.html')


@app.route('/profile')
def profile():
    if 'username' in session:
        db = createConnection()
        user = db.users.find_one({"username": session['username']})
        if user:
            return render_template('profile.html', name=user['name'], username=user['username'], scan_history=user.get('scan_history', []))
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

def fetch_ticker_info(ticker):
    try:
        ticker_info = yf.Ticker(ticker).info
        return ticker_info.get('regularMarketPrice') or ticker_info.get('previousClose', 'N/A')
    except Exception as exc:
        print(f"{ticker} generated an exception: {exc}")
        return 'N/A'

def fetch_market_data(tickers):
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_ticker_info, ticker): ticker for ticker in tickers}
        results = {}
        for future in as_completed(futures):
            ticker = futures[future]
            result = future.result()
            display_ticker = ticker.replace('^','')
            results[display_ticker] = result
    return results

@app.route('/earnings_report', methods=['GET', 'POST'])
def earnings_report():
    tickers = ['AAPL', 'GOOGL', 'MSFT', '^GSPC','^DJI','^IXIC','^RUT']
    live_market_data = fetch_market_data(tickers)
    if request.method == 'POST':
        try:
            q1 = float(request.form.get('Q1', 0))
            q2 = float(request.form.get('Q2', 0))
            q3 = float(request.form.get('Q3', 0))
            q4 = float(request.form.get('Q4', 0))
            sample_earnings['this_year'] = [q1,q2,q3,q4]
        except ValueError:
            pass
    img = quarterly_earnings()
    return render_template('earnings_report.html',image = img, data=live_market_data)




def quarterly_earnings():
    quarters = ['Q1','Q2','Q3','Q4']
    x = range(len(quarters))

    fig, ax = plt.subplots()
    ax.bar(x, sample_earnings['last_year'], width=0.35,label='Last Year')
    ax.bar(x, sample_earnings['this_year'], width=0.35,label='This Year')

    ax.set_xlabel('Quarters')
    ax.set_ylabel('Earnings ($)')
    ax.set_title('Quarterly Earnings Comparison')
    ax.set_xticks([p + 0.17 for p in x])
    ax.set_xticklabels(quarters)
    ax.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return image_base64

if __name__ == '__main__':
    app.run(debug=True)
