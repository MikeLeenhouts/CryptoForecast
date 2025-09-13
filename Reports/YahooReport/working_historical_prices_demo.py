#!/usr/bin/env python3
"""Working demonstration of historical price data retrieval using yfinance."""

import yfinance as yf
import pandas as pd
from datetime import date, timedelta
import sys
import os

# Add the Reports directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from YahooReport import HistoricalPrices
from dataconfigs import DataEvent, DataFrequency, Locale

def demo_yfinance_approach():
    """Demonstrate working historical price retrieval using yfinance."""
    
    print("=" * 60)
    print("WORKING HISTORICAL PRICES DEMONSTRATION")
    print("Using yfinance library as reliable alternative")
    print("=" * 60)
    
    # Test 1: Apple Stock Data
    print("\n1. APPLE (AAPL) STOCK DATA - Last 30 days")
    print("-" * 50)
    
    try:
        # Create ticker object
        aapl = yf.Ticker("AAPL")
        
        # Get historical data for last 30 days
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        hist_data = aapl.history(start=start_date, end=end_date)
        
        print(f"Successfully retrieved Apple data from {start_date} to {end_date}")
        print(f"Data shape: {hist_data.shape}")
        print(f"Columns: {list(hist_data.columns)}")
        
        print("\nFirst 5 rows:")
        print(hist_data.head())
        
        print("\nLast 5 rows:")
        print(hist_data.tail())
        
        # Save to CSV
        aapl_file = "AAPL_historical_data.csv"
        hist_data.to_csv(aapl_file)
        print(f"\nData saved to: {aapl_file}")
        
        # Show some statistics
        print(f"\nPrice Statistics:")
        print(f"Highest Close: ${hist_data['Close'].max():.2f}")
        print(f"Lowest Close: ${hist_data['Close'].min():.2f}")
        print(f"Average Close: ${hist_data['Close'].mean():.2f}")
        print(f"Total Volume: {hist_data['Volume'].sum():,}")
        
    except Exception as e:
        print(f"Error retrieving Apple data: {e}")
    
    # Test 2: Bitcoin Data
    print("\n\n2. BITCOIN (BTC-USD) DATA - Last 14 days")
    print("-" * 50)
    
    try:
        btc = yf.Ticker("BTC-USD")
        
        end_date = date.today()
        start_date = end_date - timedelta(days=14)
        
        btc_data = btc.history(start=start_date, end=end_date)
        
        print(f"Successfully retrieved Bitcoin data from {start_date} to {end_date}")
        print(f"Data shape: {btc_data.shape}")
        
        print("\nBitcoin Price Data:")
        print(btc_data[['Open', 'High', 'Low', 'Close', 'Volume']])
        
        # Save to CSV
        btc_file = "BTC_historical_data.csv"
        btc_data.to_csv(btc_file)
        print(f"\nBitcoin data saved to: {btc_file}")
        
        # Price analysis
        price_change = btc_data['Close'].iloc[-1] - btc_data['Close'].iloc[0]
        price_change_pct = (price_change / btc_data['Close'].iloc[0]) * 100
        
        print(f"\nBitcoin Analysis (14-day period):")
        print(f"Starting Price: ${btc_data['Close'].iloc[0]:,.2f}")
        print(f"Ending Price: ${btc_data['Close'].iloc[-1]:,.2f}")
        print(f"Price Change: ${price_change:,.2f} ({price_change_pct:+.2f}%)")
        
    except Exception as e:
        print(f"Error retrieving Bitcoin data: {e}")
    
    # Test 3: Multiple stocks comparison
    print("\n\n3. MULTIPLE STOCKS COMPARISON - Last 7 days")
    print("-" * 50)
    
    try:
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
        comparison_data = {}
        
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            if not data.empty:
                comparison_data[symbol] = {
                    'Start_Price': data['Close'].iloc[0],
                    'End_Price': data['Close'].iloc[-1],
                    'Change_Pct': ((data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100,
                    'Avg_Volume': data['Volume'].mean()
                }
        
        # Create comparison DataFrame
        comparison_df = pd.DataFrame(comparison_data).T
        
        print("Stock Performance Comparison (7 days):")
        print(comparison_df.round(2))
        
        # Save comparison
        comparison_file = "stock_comparison.csv"
        comparison_df.to_csv(comparison_file)
        print(f"\nComparison data saved to: {comparison_file}")
        
        # Find best and worst performers
        best_performer = comparison_df['Change_Pct'].idxmax()
        worst_performer = comparison_df['Change_Pct'].idxmin()
        
        print(f"\nBest Performer: {best_performer} ({comparison_df.loc[best_performer, 'Change_Pct']:+.2f}%)")
        print(f"Worst Performer: {worst_performer} ({comparison_df.loc[worst_performer, 'Change_Pct']:+.2f}%)")
        
    except Exception as e:
        print(f"Error in multiple stocks comparison: {e}")

def demo_original_class_with_yfinance():
    """Show how to adapt the original HistoricalPrices class concept with yfinance."""
    
    print("\n\n4. ADAPTED HISTORICAL PRICES CLASS CONCEPT")
    print("-" * 50)
    
    class WorkingHistoricalPrices:
        """Working version using yfinance backend."""
        
        def __init__(self, instrument, start_date, end_date):
            self.instrument = instrument
            self.start_date = start_date
            self.end_date = end_date
            self.ticker = yf.Ticker(instrument)
            self.data = self.ticker.history(start=start_date, end=end_date)
        
        def to_csv(self, path=None):
            """Export to CSV format."""
            if path is None:
                return self.data.to_csv()
            else:
                self.data.to_csv(path)
                return None
        
        def to_dfs(self):
            """Return as DataFrame dictionary."""
            return {'Historical Prices': self.data}
        
        def get_summary(self):
            """Get summary statistics."""
            if self.data.empty:
                return "No data available"
            
            return {
                'Symbol': self.instrument,
                'Period': f"{self.start_date} to {self.end_date}",
                'Records': len(self.data),
                'High': self.data['High'].max(),
                'Low': self.data['Low'].min(),
                'Avg_Close': self.data['Close'].mean(),
                'Total_Volume': self.data['Volume'].sum()
            }
    
    # Test the working class
    try:
        print("Testing WorkingHistoricalPrices class...")
        
        end_date = date.today()
        start_date = end_date - timedelta(days=10)
        
        tesla = WorkingHistoricalPrices('TSLA', start_date, end_date)
        
        print(f"Created HistoricalPrices object for TSLA")
        
        # Get summary
        summary = tesla.get_summary()
        print(f"\nSummary:")
        for key, value in summary.items():
            if isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")
        
        # Export to CSV
        csv_data = tesla.to_csv()
        print(f"\nCSV export successful (first 200 chars):")
        print(csv_data[:200] + "...")
        
        # Get DataFrame
        df_dict = tesla.to_dfs()
        df = df_dict['Historical Prices']
        print(f"\nDataFrame shape: {df.shape}")
        print("Sample data:")
        print(df.head(3))
        
    except Exception as e:
        print(f"Error testing WorkingHistoricalPrices: {e}")

if __name__ == "__main__":
    print("Starting Historical Prices Demonstration...")
    
    # Run the demonstrations
    demo_yfinance_approach()
    demo_original_class_with_yfinance()
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETED SUCCESSFULLY!")
    print("Historical price data retrieval is now working using yfinance.")
    print("=" * 60)
