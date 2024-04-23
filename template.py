from flask import Flask, render_template_string
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

def extract_risk_factors(text, start_pattern, end_pattern):
    # Find the first occurrence of the start pattern
    first_occurrence_index = text.find(start_pattern)
    
    # Find the second occurrence of the start pattern
    start_index = text.find(start_pattern, first_occurrence_index + len(start_pattern))
    end_index = text.find(end_pattern, start_index)
    
    if start_index != -1 and end_index != -1:
        return text[start_index:end_index].strip()
    elif start_index != -1:
        return text[start_index:start_index + 1500].strip()
    else:
        return "Risk Factors section not found."


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
    </style>
    <title>Quarterly Earnings Report</title>
</head>
<body>
    <div class="report-container">
        <h1>Quarterly Earnings Report</h1>
        <table>
            <tr>
                <th>Financial Metric</th>
                <th>Value (in million USD)</th>
            </tr>
            <!-- The initial financial metrics table as before -->
            <tr>
                <td>Net Sales</td>
                <td>{{ net_sales }}</td>
            </tr>
            <tr>
                <td>Operating Income</td>
                <td>{{ operating_income }}</td>
            </tr>
            <tr>
                <td>Net Income</td>
                <td>{{ net_income }}</td>
            </tr>
            <!-- Add more rows for other data points -->
        </table>
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
        <!-- Rows with balance sheet data for 2022 and 2023 will be dynamically inserted here -->
    </table>
</div>


   <!-- Consolidated Statements of Operations table -->
<div class="report-container">
    <h2>Consolidated Statements of Operations</h2>
    <table>
        <tr>
            <th style="background-color: #ff0000;">Financial Metric</th>
            <th style="background-color: #ff0000;">2022 (in million USD)</th>
            <th style="background-color: #ff0000;">2023 (in million USD)</th>
        </tr>
        <!-- Rows with statements of operations data will be dynamically inserted here -->
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
        <!-- Rows with cash flows data will be dynamically inserted here -->
    </table>
</div>


    <!-- Existing Risk Factors section -->
    <div class="report-container">
        <h2>Risk Factors</h2>
        <p>{{ risk_factors }}</p>
    </div>
</body>
</html>
"""

    return render_template_string(html_template, **data)

if __name__ == '__main__':
    app.run(debug=True)