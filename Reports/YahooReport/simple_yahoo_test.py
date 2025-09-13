#!/usr/bin/env python3
"""Simple test to verify Yahoo Finance data retrieval works."""

import requests
import pandas as pd
from datetime import date, timedelta
from io import StringIO

def test_yahoo_direct():
    """Test direct Yahoo Finance API call without cookies."""
    
    print("Testing direct Yahoo Finance API access...")
    print("=" * 50)
    
    # Calculate date range (last 30 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # Convert to Unix timestamps
    min_date = date(1970, 1, 1)
    start_period = int((start_date - min_date).total_seconds())
    end_period = int((end_date - min_date).total_seconds())
    
    # Test with Apple stock
    symbol = 'AAPL'
    url = f'https://query1.finance.yahoo.com/v7/finance/download/{symbol}'
    
    params = {
        'period1': start_period,
        'period2': end_period,
        'interval': '1d',
        'events': 'history',
        'includeAdjustedClose': 'true'
    }
    
    print(f"Requesting data for {symbol} from {start_date} to {end_date}")
    print(f"URL: {url}")
    print(f"Parameters: {params}")
    print("-" * 50)
    
    try:
        # Try without cookies first
        response = requests.get(url, params=params)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("Success! Data retrieved without cookies.")
            
            # Parse the CSV data
            csv_data = response.text
            print(f"Raw data preview (first 300 characters):")
            print(csv_data[:300])
            print("...")
            
            # Convert to DataFrame
            df = pd.read_csv(StringIO(csv_data))
            print(f"\nDataFrame shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            
            if not df.empty:
                print(f"\nFirst 5 rows:")
                print(df.head())
                
                print(f"\nLast 5 rows:")
                print(df.tail())
                
                # Save to file
                output_file = f"{symbol}_data.csv"
                df.to_csv(output_file, index=False)
                print(f"\nData saved to: {output_file}")
                
                return True
            else:
                print("DataFrame is empty!")
                return False
                
        else:
            print(f"Failed with status code: {response.status_code}")
            print(f"Response text: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"Error occurred: {e}")
        return False

def test_alternative_approach():
    """Test alternative approach using yfinance-like method."""
    
    print("\n\nTesting alternative approach...")
    print("=" * 50)
    
    try:
        # Try to get basic quote data first
        symbol = 'AAPL'
        quote_url = f'https://finance.yahoo.com/quote/{symbol}'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(quote_url, headers=headers)
        print(f"Quote page status: {response.status_code}")
        
        if response.status_code == 200:
            print("Successfully accessed Yahoo Finance quote page")
            
            # Look for cookies in the response
            cookies = response.cookies
            print(f"Cookies received: {dict(cookies)}")
            
            if 'B' in cookies:
                print(f"Found B cookie: {cookies['B']}")
                
                # Now try the download with the cookie
                end_date = date.today()
                start_date = end_date - timedelta(days=7)  # Shorter period
                min_date = date(1970, 1, 1)
                start_period = int((start_date - min_date).total_seconds())
                end_period = int((end_date - min_date).total_seconds())
                
                download_url = f'https://query1.finance.yahoo.com/v7/finance/download/{symbol}'
                params = {
                    'period1': start_period,
                    'period2': end_period,
                    'interval': '1d',
                    'events': 'history'
                }
                
                download_response = requests.get(download_url, params=params, cookies=cookies, headers=headers)
                print(f"Download response status: {download_response.status_code}")
                
                if download_response.status_code == 200:
                    csv_data = download_response.text
                    print(f"Success! Retrieved data with cookie:")
                    print(csv_data[:200])
                    
                    df = pd.read_csv(StringIO(csv_data))
                    print(f"DataFrame shape: {df.shape}")
                    print(df.head())
                    return True
                else:
                    print(f"Download failed: {download_response.text[:200]}")
            else:
                print("No B cookie found in response")
        else:
            print(f"Failed to access quote page: {response.status_code}")
            
    except Exception as e:
        print(f"Alternative approach error: {e}")
        
    return False

if __name__ == "__main__":
    print("Yahoo Finance API Testing")
    print("=" * 60)
    
    # Test 1: Direct API call
    success1 = test_yahoo_direct()
    
    # Test 2: Alternative approach with cookies
    if not success1:
        success2 = test_alternative_approach()
        
        if not success2:
            print("\n" + "=" * 60)
            print("SUMMARY: Both approaches failed.")
            print("This might be due to Yahoo Finance API restrictions.")
            print("Consider using alternative libraries like yfinance.")
    else:
        print("\n" + "=" * 60)
        print("SUCCESS: Direct API access worked!")
