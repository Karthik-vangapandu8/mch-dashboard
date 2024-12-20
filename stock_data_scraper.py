import threading
import queue
import time
import random
import pandas as pd
import requests
from datetime import datetime, timedelta
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
import logging
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class StockDataScraper:
    def __init__(self, symbols, start_date, end_date, max_workers=5):
        """
        Initialize the stock data scraper.
        
        Args:
            symbols (list): List of stock symbols to scrape
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str): End date in 'YYYY-MM-DD' format
            max_workers (int): Maximum number of concurrent threads
        """
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.max_workers = max_workers
        self.data_queue = queue.Queue()
        self.error_queue = queue.Queue()
        self.results = {}
        self.lock = threading.Lock()

    def download_stock_data(self, symbol):
        """
        Download historical stock data for a given symbol.
        Uses threading to handle multiple downloads concurrently.
        """
        try:
            logging.info(f"Downloading data for {symbol}")
            
            # Add random delay to prevent rate limiting
            time.sleep(random.uniform(0.1, 0.5))
            
            # Download data using yfinance
            stock = yf.Ticker(symbol)
            df = stock.history(
                start=self.start_date,
                end=self.end_date
            )
            
            # Basic data validation
            if df.empty:
                raise ValueError(f"No data available for {symbol}")
            
            # Calculate additional metrics
            df['Daily_Return'] = df['Close'].pct_change()
            df['Volatility'] = df['Daily_Return'].rolling(window=20).std()
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            
            # Put the processed data in the queue
            self.data_queue.put((symbol, df))
            logging.info(f"Successfully processed {symbol}")
            
        except Exception as e:
            logging.error(f"Error processing {symbol}: {str(e)}")
            self.error_queue.put((symbol, str(e)))

    def save_to_csv(self, symbol, df):
        """
        Save the downloaded data to a CSV file.
        Uses a lock to prevent multiple threads from writing simultaneously.
        """
        try:
            with self.lock:
                filename = f"stock_data_{symbol}_{self.start_date}_{self.end_date}.csv"
                df.to_csv(filename)
                logging.info(f"Saved data for {symbol} to {filename}")
        except Exception as e:
            logging.error(f"Error saving data for {symbol}: {str(e)}")

    def calculate_metrics(self, df):
        """
        Calculate various financial metrics for the stock data.
        """
        metrics = {
            'avg_volume': df['Volume'].mean(),
            'avg_price': df['Close'].mean(),
            'volatility': df['Daily_Return'].std() * (252 ** 0.5),  # Annualized volatility
            'max_price': df['High'].max(),
            'min_price': df['Low'].min(),
            'price_range': df['High'].max() - df['Low'].min(),
            'trading_days': len(df)
        }
        return metrics

    def process_results(self):
        """
        Process all downloaded data and generate summary metrics.
        """
        while not self.data_queue.empty():
            symbol, df = self.data_queue.get()
            
            # Calculate metrics
            metrics = self.calculate_metrics(df)
            
            # Store results
            with self.lock:
                self.results[symbol] = metrics
            
            # Save to CSV
            self.save_to_csv(symbol, df)
            
            self.data_queue.task_done()

    def generate_report(self):
        """
        Generate a summary report of all processed data.
        """
        report = {
            'successful_downloads': len(self.results),
            'failed_downloads': self.error_queue.qsize(),
            'metrics_by_symbol': self.results,
            'errors': {}
        }
        
        # Add errors to report
        while not self.error_queue.empty():
            symbol, error = self.error_queue.get()
            report['errors'][symbol] = error
        
        # Save report to JSON
        with open('stock_analysis_report.json', 'w') as f:
            json.dump(report, f, indent=4)
        
        return report

    def run(self):
        """
        Run the complete stock data scraping process using thread pool.
        """
        start_time = time.time()
        logging.info(f"Starting data download for {len(self.symbols)} symbols")
        
        # Download data using thread pool
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            executor.map(self.download_stock_data, self.symbols)
        
        # Process results
        self.process_results()
        
        # Generate report
        report = self.generate_report()
        
        end_time = time.time()
        duration = end_time - start_time
        
        logging.info(f"Completed processing in {duration:.2f} seconds")
        logging.info(f"Successfully processed: {report['successful_downloads']} symbols")
        logging.info(f"Failed to process: {report['failed_downloads']} symbols")
        
        return report

def main():
    # Example usage
    symbols = [
        'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META',
        'TSLA', 'NVDA', 'JPM', 'V', 'WMT'
    ]
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    # Initialize and run scraper
    scraper = StockDataScraper(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        max_workers=5
    )
    
    report = scraper.run()
    
    # Print summary metrics for each successfully downloaded stock
    print("\nSummary Metrics:")
    print("-" * 50)
    for symbol, metrics in report['metrics_by_symbol'].items():
        print(f"\n{symbol}:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.2f}")
    
    # Print any errors that occurred
    if report['errors']:
        print("\nErrors:")
        print("-" * 50)
        for symbol, error in report['errors'].items():
            print(f"{symbol}: {error}")

if __name__ == "__main__":
    main()
