#!/usr/bin/env python3
"""Retrieve historical price data for a specific asset and date(s) using yfinance."""

import yfinance as yf
import pandas as pd
import datetime as dt  # Alias the module to avoid shadowing
import sys
import os
from typing import Union, List, Dict

# Add the Reports directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Debug: Print type of dt.date to check for shadowing
print(f"Debug: Type of 'dt.date' is {type(dt.date)}")

def get_asset_prices(asset_symbol: str, dates: Union[str, dt.date, List[Union[str, dt.date]]]) -> Union[float, Dict[str, float], None]:
    """
    Retrieve closing price(s) for a given asset on specified date(s) using yfinance.

    Args:
        asset_symbol (str): Yahoo Finance ticker symbol (e.g., 'AAPL', 'BTC-USD', 'GC=F').
        dates (str, dt.date, or list): Single date (YYYY-MM-DD or dt.date object) or list of dates.

    Returns:
        float: Closing price for a single date, or None if not found.
        dict: Dictionary of date (YYYY-MM-DD) to closing price for multiple dates.
        None: If an error occurs or no data is available.
    """
    try:
        # Initialize ticker
        ticker = yf.Ticker(asset_symbol)

        # Convert single date to list for consistent processing
        if isinstance(dates, (str, dt.date)):
            dates = [dates]
        
        # Convert string dates to dt.date objects and ensure YYYY-MM-DD format
        date_objects = []
        for d in dates:
            if isinstance(d, str):
                try:
                    d = dt.datetime.strptime(d, '%Y-%m-%d').date()
                except ValueError:
                    print(f"Error: Invalid date format for {d}. Use YYYY-MM-DD.")
                    return None
            date_objects.append(d)

        # Determine date range to fetch (add 1 day to include end date)
        start_date = min(date_objects)
        end_date = max(date_objects) + dt.timedelta(days=1)

        # Fetch historical data
        hist_data = ticker.history(start=start_date, end=end_date)

        if hist_data.empty:
            print(f"No data available for {asset_symbol} from {start_date} to {end_date}.")
            return None

        # Filter to requested dates and get closing prices
        results = {}
        for d in date_objects:
            date_str = d.strftime('%Y-%m-%d')
            # Yahoo Finance uses date as index; filter by date
            if date_str in hist_data.index.strftime('%Y-%m-%d'):
                close_price = hist_data.loc[date_str, 'Close']
                results[date_str] = round(float(close_price), 2)
            else:
                results[date_str] = None
                print(f"Warning: No data for {asset_symbol} on {date_str}.")

        # Save to CSV
        output_dir = r"C:\Users\mikel\OneDrive\_Projects\CryptoForecast\CryptoForecastSolution\Reports"
        os.makedirs(output_dir, exist_ok=True)
        csv_file = os.path.join(output_dir, f"{asset_symbol}_prices.csv")
        pd.DataFrame.from_dict(results, orient='index', columns=['Close']).to_csv(csv_file)
        print(f"Data saved to: {csv_file}")

        # Return single price if single date requested, else dictionary
        if len(dates) == 1:
            return results[date_objects[0].strftime('%Y-%m-%d')]
        return results

    except Exception as e:
        print(f"Error retrieving data for {asset_symbol}: {e}")
        return None

def demo_get_asset_prices():
    """Demonstrate retrieving asset prices for specific dates."""
    
    print("=" * 60)
    print("ASSET PRICE RETRIEVAL DEMONSTRATION")
    print("Using yfinance to fetch prices for specific dates")
    print("=" * 60)

    # Test 1: Single date, Bitcoin
    print("\n1. BITCOIN (BTC-USD) - Single Date (2025-08-01)")
    print("-" * 50)
    result = get_asset_prices("BTC-USD", "2025-08-01")
    print(f"Bitcoin price on 2025-08-01: {result if result is not None else 'No data'}")

    # Test 2: Multiple dates, Apple
    print("\n2. APPLE (AAPL) - Multiple Dates")
    print("-" * 50)
    dates = ["2025-08-01", "2025-08-04", "2025-08-05"]
    result = get_asset_prices("AAPL", dates)
    print("Apple prices:")
    if result:
        for date, price in result.items():
            print(f"{date}: {price if price is not None else 'No data'}")

    # Test 3: Gold futures, single date
    print("\n3. GOLD (GC=F) - Single Date (2025-08-01)")
    print("-" * 50)
    result = get_asset_prices("GC=F", dt.date(2025, 8, 1))
    print(f"Gold price on 2025-08-01: {result if result is not None else 'No data'}")

    # Test 4: Invalid symbol
    print("\n4. INVALID SYMBOL (XYZ) - Single Date")
    print("-" * 50)
    result = get_asset_prices("XYZ", "2025-08-01")
    print(f"Price for XYZ on 2025-08-01: {result if result is not None else 'No data'}")

if __name__ == "__main__":
    print("Starting Asset Price Retrieval Demonstration...")
    demo_get_asset_prices()
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)