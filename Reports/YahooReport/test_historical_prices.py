#!/usr/bin/env python3
"""Test script to demonstrate HistoricalPrices functionality."""

import sys
import os
from datetime import date, timedelta

# Add the Reports directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from YahooReport import HistoricalPrices
from dataconfigs import DataEvent, DataFrequency, Locale

def test_historical_prices():
    """Test the HistoricalPrices functionality with various examples."""
    
    print("Testing HistoricalPrices functionality...")
    print("=" * 50)
    
    # Test 1: Get Apple stock data for the last 30 days
    print("\n1. Testing Apple (AAPL) stock - Last 30 days")
    print("-" * 40)
    
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    try:
        apple_data = HistoricalPrices(
            instrument='AAPL',
            start_date=start_date,
            end_date=end_date,
            frequency=DataFrequency.DAILY
        )
        
        print(f"Successfully retrieved Apple data from {start_date} to {end_date}")
        
        # Convert to DataFrame and display first few rows
        df_dict = apple_data.to_dfs()
        apple_df = df_dict['Historical Prices']
        print(f"Data shape: {apple_df.shape}")
        print("\nFirst 5 rows:")
        print(apple_df.head())
        
        # Save to CSV
        csv_output = apple_data.to_csv()
        print(f"\nCSV data preview (first 200 characters):")
        print(csv_output[:200] + "...")
        
    except Exception as e:
        print(f"Error retrieving Apple data: {e}")
    
    # Test 2: Get Bitcoin data (BTC-USD)
    print("\n\n2. Testing Bitcoin (BTC-USD) - Last 7 days")
    print("-" * 40)
    
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    
    try:
        btc_data = HistoricalPrices(
            instrument='BTC-USD',
            start_date=start_date,
            end_date=end_date,
            frequency=DataFrequency.DAILY
        )
        
        print(f"Successfully retrieved Bitcoin data from {start_date} to {end_date}")
        
        # Convert to DataFrame
        df_dict = btc_data.to_dfs()
        btc_df = df_dict['Historical Prices']
        print(f"Data shape: {btc_df.shape}")
        print("\nBitcoin price data:")
        print(btc_df[['Open', 'High', 'Low', 'Close', 'Volume']])
        
    except Exception as e:
        print(f"Error retrieving Bitcoin data: {e}")
    
    # Test 3: Get Tesla data with string dates
    print("\n\n3. Testing Tesla (TSLA) with string dates - Last 14 days")
    print("-" * 40)
    
    end_date_str = date.today().strftime("%Y-%m-%d")
    start_date_str = (date.today() - timedelta(days=14)).strftime("%Y-%m-%d")
    
    try:
        tesla_data = HistoricalPrices(
            instrument='TSLA',
            start_date=start_date_str,
            end_date=end_date_str,
            date_format_string="%Y-%m-%d",
            frequency=DataFrequency.DAILY
        )
        
        print(f"Successfully retrieved Tesla data from {start_date_str} to {end_date_str}")
        
        # Save to file
        tesla_data.to_csv('tesla_historical_data.csv')
        print("Tesla data saved to 'tesla_historical_data.csv'")
        
        # Show summary statistics
        df_dict = tesla_data.to_dfs()
        tesla_df = df_dict['Historical Prices']
        print(f"\nTesla data summary:")
        print(tesla_df.describe())
        
    except Exception as e:
        print(f"Error retrieving Tesla data: {e}")
    
    print("\n" + "=" * 50)
    print("HistoricalPrices testing completed!")

if __name__ == "__main__":
    test_historical_prices()
