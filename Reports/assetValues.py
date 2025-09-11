import requests
import pandas as pd
from datetime import datetime, timedelta

# API keys (replace with your own)
ALPHA_VANTAGE_API_KEY = "YOUR_ALPHA_VANTAGE_API_KEY"  # Get at https://www.alphavantage.co/support/#api-key
QUANDL_API_KEY = "YOUR_QUANDL_API_KEY"  # Get at https://data.nasdaq.com/

# Date range for November 2024
start_date = datetime(2024, 11, 1)
end_date = datetime(2024, 11, 30)
dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

# Initialize data dictionary
data = {'Date': [d.strftime('%Y-%m-%d') for d in dates], 
        'Bitcoin_Close_USD': [None] * len(dates), 
        'Ethereum_Close_USD': [None] * len(dates), 
        'Gold_Close_USD': [None] * len(dates)}

# Fetch Bitcoin and Ethereum from Alpha Vantage
for crypto in [('BTC', 'Bitcoin_Close_USD'), ('ETH', 'Ethereum_Close_USD')]:
    url = f"https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol={crypto[0]}&market=USD&month=2024-11&outputsize=full&apikey={ALPHA_VANTAGE_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        response_json = response.json()
        time_series = response_json.get("Time Series (Digital Currency Daily)", {})
        if not time_series:
            print(f"Error fetching {crypto[0]}: {response_json.get('Error Message', 'No time series data in response')}")
            print(f"Full response: {response_json}")
            continue
        for date, values in time_series.items():
            if date in data['Date']:
                idx = data['Date'].index(date)
                # Try multiple possible keys for closing price
                close_price = None
                for key in ["4a. close (USD)", "4. close (USD)", "4. close"]:
                    if key in values:
                        close_price = float(values[key])
                        break
                if close_price is not None:
                    data[crypto[1]][idx] = close_price
                else:
                    print(f"Closing price key not found for {crypto[0]} on {date}. Available keys: {list(values.keys())}")
    else:
        print(f"Error fetching {crypto[0]}: HTTP {response.status_code}, {response.text}")

# Fetch Gold from Alpha Vantage (try GOLD endpoint)
url = f"https://www.alphavantage.co/query?function=GOLD&month=2024-11&apikey={ALPHA_VANTAGE_API_KEY}"
response = requests.get(url)
if response.status_code == 200 and "Time Series" in response.json():
    response_json = response.json()
    time_series = response_json.get("Time Series", {})
    for date, values in time_series.items():
        if date in data['Date']:
            idx = data['Date'].index(date)
            # Try possible keys for gold closing price
            close_price = None
            for key in ["4. close", "4a. close (USD)", "close"]:
                if key in values:
                    close_price = float(values[key])
                    break
            if close_price is not None:
                data['Gold_Close_USD'][idx] = close_price
            else:
                print(f"Gold closing price key not found on {date}. Available keys: {list(values.keys())}")
else:
    # Fallback to Quandl for daily gold prices (LBMA)
    print("Falling back to Quandl for Gold prices")
    url = f"https://data.nasdaq.com/api/v3/datasets/LBMA/GOLD/data?start_date=2024-11-01&end_date=2024-11-30&api_key={QUANDL_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        gold_data = response.json().get('dataset_data', {}).get('data', [])
        for entry in gold_data:
            date = entry[0]  # Date in YYYY-MM-DD
            if date in data['Date']:
                idx = data['Date'].index(date)
                data['Gold_Close_USD'][idx] = float(entry[1])  # LBMA gold price (USD/oz)
    else:
        print(f"Error fetching Gold from Quandl: HTTP {response.status_code}, {response.text}")

# Save to CSV
output_path = r"C:\Users\mikel\OneDrive\_Projects\CryptoForecast\CryptoForecastSolution\Reports\crypto_gold_nov2024.csv"
pd.DataFrame(data).to_csv(output_path, index=False)
print(f"Data saved to {output_path}")