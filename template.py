from flask import Flask, render_template_string
import yfinance as yf
import fitz  # PyMuPDF
import re

app = Flask(__name__)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    with fitz.open(pdf_path) as pdf:
        text = ""
        for page in pdf:
            text += page.get_text()
    return text

# Function to parse relevant data from text
def parse_financial_data(text):
    patterns = {
        'net_sales': r'Net sales .+\$(\d+\.\d+) billion',
        'operating_income': r'Operating income .+\$(\d+\.\d+) billion',
        'net_income': r'Net income .+\$(\d+\.\d+) billion',
    }
    data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        data[key] = match.group(1) if match else "Not found"
    return data

@app.route('/report')
def report():
    pdf_path = 'AmazonEarnings.pdf'
    text = extract_text_from_pdf(pdf_path)
    data = parse_financial_data(text)

    tickerSymbol = 'MSFT'  # Example for Microsoft Corporation
    tickerData = yf.Ticker(tickerSymbol)
    ticker_info = tickerData.info

    # Fetch live market data for the indices and commodities
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
        individual_ticker_info = yf.Ticker(ticker).info  # Get the info for each market ticker
        # Fallback to 'previousClose' if 'regularMarketPrice' is not available, then to 'N/A'
        live_market_data[name] = individual_ticker_info.get('regularMarketPrice') or individual_ticker_info.get('previousClose', 'N/A')


    other_ticker_data = {
        'ticker': tickerSymbol,
        'current_price': ticker_info['currentPrice'],
        'pe_ratio': ticker_info.get('trailingPE', 'N/A'),
        'week_change': ticker_info.get('52WeekChange', 'N/A'),
        'earnings_growth': ticker_info.get('earningsGrowth', 'N/A'),
    }

    # Prepare the final data to pass to the template
    final_data = {
        'data': data,  # Financial data from the PDF
        'ticker_info': other_ticker_data,  # Information about Microsoft stock
        'live_market_data': live_market_data,  # Live market data for indices and commodities
    }

    html_template = """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f4f4;
            margin: 0;
            padding: 20px;
        }
        .report-container {
            background: #fff;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 10px;
            text-align: left;
        }
        th {
            background-color: #4CAF50;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        h1 {
            text-align: center;
        }
    </style>
    <title>Quarterly Earnings Report</title>
</head>
<body>
     <!-- Live Market Data Bar section -->
        <div class="market-data-container">
            <h2>Live Market Data</h2>
            <div style="background-color: #f4f4f4; padding: 10px; margin-bottom: 20px;">
                {% for name, value in live_market_data.items() %}
                <span><strong>{{ name }}</strong>: {{ value }}</span> |
                {% endfor %}
            </div>
        </div>
        
    <h1>Quarterly Earnings Report</h1>
    <div class="report-container">   
        <h2>{{ ticker_info.ticker }} Stock Information</h2>
        <p>Current Price: {{ ticker_info.current_price }}</p>
        <p>P/E Ratio: {{ ticker_info.pe_ratio }}</p>
        <p>52-Week Change: {{ ticker_info.week_change }}</p>
        <p>Earnings Growth: {{ ticker_info.earnings_growth }}</p>
    </div>

    <!-- Consolidated Balance Sheets table -->
<div class="report-container">
    <h2>Consolidated Balance Sheets</h2>
    <table>
        <tr>
            <th style="background-color: #337ab7;">Financial Metric</th>
            <th style="background-color: #337ab7;">2022 (in million USD)</th>
            <th style="background-color: #337ab7;">2023 (in million USD)</th>
        </tr>
        <tr>
            <td>Total Current Assets</td>
            <td>{{ current_assets_2022 }}</td>
            <td>{{ current_assets_2023 }}</td>
        </tr>
        <tr>
            <td>Total Assets</td>
            <td>{{ total_assets_2022 }}</td>
            <td>{{ total_assets_2023 }}</td>
        </tr>
        <tr>
            <td>Total Current Liabilities</td>
            <td>{{ total_current_liabilities_2022 }}</td>
            <td>{{ total_current_liabilities_2023 }}</td>
        </tr>
        <tr>
            <td>Total Stockholders' Equity</td>
            <td>{{ total_current_liabilities_2022 }}</td>
            <td>{{ total_current_liabilities_2023 }}</td>
        </tr>
        <tr>
            <td>Total Liabilities and Stockholders' Equity</td>
            <td>{{ total_liabilities_and_stockholders_equity_2022 }}</td>
            <td>{{ total_liabilities_and_stockholders_equity_2023 }}</td>
        </tr>
    </table>
</div>

   <!-- Consolidated Statements of Operations table -->
<div class="report-container">
    <h2>Consolidated Statements of Operations </h2>
    <table>
        <tr>
            <th style="background-color: #ff0000;">Financial Metric</th>
            <th style="background-color: #ff0000;">2022 (in million USD)</th>
            <th style="background-color: #ff0000;">2023 (in million USD)</th>
        </tr>
        <tr>
            <td>CASH, CASH EQUIVALENTS, AND RESTRICTED CASH, BEGINNING OF PERIOD</td>
            <td>{{ cash_beginning_2022 }}</td>
            <td>{{ cash_beginning_2023 }}</td>
        </tr>
        <tr>
            <td>Net income (loss)</td>
            <td>{{ net_income_2022 }}</td>
            <td>{{ net_income_2023 }}</td>
        </tr>
        <tr>
            <td>Net cash provided by (used in) operating activities</td>
            <td>{{ net_operating_cash_2022 }}</td>
            <td>{{ net_operating_cash_2023 }}</td>
        </tr>
        <tr>
            <td>Net cash used in investing activities</td>
            <td>{{ net_investing_cash_2022 }}</td>
            <td>{{ net_investing_cash_2023 }}</td>
        </tr>
        <tr>
            <td>Net cash provided by (used in) financing activities</td>
            <td>{{ net_financing_cash_2022 }}</td>
            <td>{{ net_financing_cash_2023 }}</td>
        </tr>
        <tr>
            <td>CASH, CASH EQUIVALENTS, AND RESTRICTED CASH, END OF PERIOD</td>
            <td>{{ cash_beginning_2022 }}</td>
            <td>{{ cash_beginning_2023 }}</td>
        </tr>
    <table>
</div>

    </table>
</div>

    <!-- Consolidated Statements of Cash Flows table -->
<div class="report-container">
    <h2>Consolidated Statements of Cash Flows</h2>
    <table>
        <tr>
            <th style="background-color: #f0ad4e;">Financial Metric</th>
            <th style="background-color: #f0ad4e;">2022 (in million USD)</th>
            <th style="background-color: #f0ad4e;">2023 (in million USD)</th>
        </tr>
        <tr>
            <td>Total Net Sales</td>
            <td>{{ total_net_sales_2022 }}</td>
            <td>{{ total_net_sales_2023 }}</td>
        </tr>
        <tr>
            <td>Total Operating Expenses</td>
            <td>{{ total_operating_expenses_2022 }}</td>
            <td>{{ total_operating_expenses_2023 }}</td>
        </tr>
        <tr>
            <td>Net income (loss)</td>
            <td>{{ net_operating_cash_2022 }}</td>
            <td>{{ net_operating_cash_2023 }}</td>
        </tr>
        <tr>
            <td>Basic Earnings Per Share</td>
            <td>{{ basic_earnings_per_share_2022 }}</td>
            <td>{{ basic_earnings_per_share_2023 }}</td>
        </tr>
        <tr>
            <td>Diluted Earnings Per Share</td>
            <td>{{ diluted_earnings_per_share_2022 }}</td>
            <td>{{ diluted_earnings_per_share_2023 }}</td>
        </tr>
    <table>
</div>
</body>
</html>
"""
    return render_template_string(html_template, **final_data)

if __name__ == '__main__':
    app.run(debug=True, port = 5001)
