import requests
import json
import sys
from datetime import datetime
import argparse
import time

class HypixelBazaarAnalyzer:
    def __init__(self):
        """
        Initialize the analyzer
        """
        self.item_ids = []
        self.bazaar_data = {}
        self.profit_opportunities = []
    
    def fetch_all_apis(self):
        """
        Try multiple possible API endpoints to get bazaar data
        """
        # List of potential API endpoints to try
        api_endpoints = [
            {
                'url': 'https://api.hypixel.net/skyblock/bazaar',
                'description': 'Hypixel Direct API (skyblock/bazaar)'
            },
            {
                'url': 'https://api.hypixel.net/resources/skyblock/bazaar',
                'description': 'Hypixel Resources API (resources/skyblock/bazaar)'
            },
            {
                'url': 'https://sky.shiiyu.moe/api/v2/bazaar',
                'description': 'SkyCrypt API (sky.shiiyu.moe)'
            },
            {
                'url': 'https://api.slothpixel.me/api/skyblock/bazaar',
                'description': 'Slothpixel API'
            },
            {
                'url': 'https://api.hysky.dev/bazaar',
                'description': 'HySky API'
            }
        ]
        
        print("Attempting to fetch Bazaar data from multiple sources...")
        
        for api in api_endpoints:
            print(f"\nTrying: {api['description']} - {api['url']}")
            success = self.try_fetch_from_api(api['url'])
            if success:
                print(f"Successfully fetched data from {api['description']}")
                return True
                
        print("All API attempts failed. Could not fetch Bazaar data.")
        return False
    
    def try_fetch_from_api(self, url):
        """
        Try to fetch data from a specific API URL
        """
        try:
            response = requests.get(url, timeout=10)
            print(f"Response status code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Failed with HTTP {response.status_code}")
                return False
            
            # Try to parse JSON
            try:
                data = response.json()
            except json.JSONDecodeError:
                print("Failed to parse response as JSON")
                return False
            
            # Save raw response for debugging
            with open('last_bazaar_response.json', 'w') as f:
                json.dump(data, f, indent=2)
            print("Saved raw response to last_bazaar_response.json")
            
            # Check response structure and extract data
            # Different APIs have different structures, so try various patterns
            
            # Pattern 1: Direct products dictionary (Hypixel API format)
            if 'products' in data:
                self.bazaar_data = data['products']
                self.item_ids = list(self.bazaar_data.keys())
                print(f"Found {len(self.item_ids)} items in 'products' field")
                return True
                
            # Pattern 2: SkyCrypt API format with bazaar field
            elif 'success' in data and data['success'] and 'bazaar' in data:
                self.bazaar_data = data['bazaar']
                self.item_ids = list(self.bazaar_data.keys())
                print(f"Found {len(self.item_ids)} items in 'bazaar' field")
                return True
                
            # Pattern 3: Direct dictionary of items (some APIs)
            elif isinstance(data, dict) and len(data) > 20:
                # Assume it's a dictionary of items if it has many keys
                self.bazaar_data = data
                self.item_ids = list(self.bazaar_data.keys())
                print(f"Found {len(self.item_ids)} items in top-level dictionary")
                return True
                
            else:
                print("Unexpected API response structure")
                print(f"Keys in response: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                return False
                
        except Exception as e:
            print(f"Error fetching from API: {e}")
            return False
    
    def load_from_file(self, filename):
        """
        Load bazaar data from a previously saved JSON file
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            print(f"Loaded data from file: {filename}")
            
            # Try to determine the structure of the saved data
            if 'products' in data:
                self.bazaar_data = data['products']
            elif 'bazaar' in data:
                self.bazaar_data = data['bazaar']
            elif isinstance(data, list) and len(data) > 0 and 'item_id' in data[0]:
                # This is likely a saved list of profit opportunities
                self.profit_opportunities = data
                print(f"Loaded {len(self.profit_opportunities)} profit opportunities from file")
                return True
            else:
                # Assume it's a direct dictionary of bazaar items
                self.bazaar_data = data
            
            self.item_ids = list(self.bazaar_data.keys())
            print(f"Found {len(self.item_ids)} items")
            return True
            
        except Exception as e:
            print(f"Error loading from file: {e}")
            return False
    
    def calculate_profit_margins(self):
        """
        Calculate various profit margins for each item
        """
        if not self.bazaar_data:
            print("No bazaar data available. Fetch data first.")
            return
        
        results = []
        processed_count = 0
        error_count = 0
        
        # Process each item we have IDs for
        for item_id in self.item_ids:
            try:
                # Skip if this item isn't in the bazaar data
                if item_id not in self.bazaar_data:
                    continue
                
                item_data = self.bazaar_data[item_id]
                
                # Different APIs might have different structures, so handle multiple cases
                buy_summary = []
                sell_summary = []
                quick_status = {}
                
                # Case 1: Standard Hypixel API format
                if 'buy_summary' in item_data and 'sell_summary' in item_data:
                    buy_summary = item_data.get('buy_summary', [])
                    sell_summary = item_data.get('sell_summary', [])
                    quick_status = item_data.get('quick_status', {})
                
                # Case 2: Some APIs have different field names
                elif 'buyOrders' in item_data and 'sellOrders' in item_data:
                    buy_summary = item_data.get('buyOrders', [])
                    sell_summary = item_data.get('sellOrders', [])
                    
                    # Adapt to different field structure
                    buy_summary = [{
                        'pricePerUnit': order.get('pricePerUnit', 0) 
                        if isinstance(order, dict) else order
                    } for order in buy_summary]
                    
                    sell_summary = [{
                        'pricePerUnit': order.get('pricePerUnit', 0)
                        if isinstance(order, dict) else order
                    } for order in sell_summary]
                    
                    # Simulate quick_status
                    quick_status = {
                        'buyPrice': buy_summary[0]['pricePerUnit'] if buy_summary else 0,
                        'sellPrice': sell_summary[0]['pricePerUnit'] if sell_summary else 0,
                        'buyVolume': item_data.get('buyVolume', 0),
                        'sellVolume': item_data.get('sellVolume', 0)
                    }
                
                # Skip items with no data
                if not buy_summary or not sell_summary:
                    continue
                
                # Get the best buy and sell orders
                # In Hypixel's API:
                # - buy_summary: Players offering to BUY from you (you SELL to them)
                # - sell_summary: Players offering to SELL to you (you BUY from them)
                best_buy_price = sell_summary[0]['pricePerUnit'] if sell_summary else 0  # Price you buy at
                best_sell_price = buy_summary[0]['pricePerUnit'] if buy_summary else 0   # Price you sell at
                
                # Get quick prices if available (swap these too for consistency)
                quick_buy = quick_status.get('sellPrice', best_buy_price)
                quick_sell = quick_status.get('buyPrice', best_sell_price)
                
                # Calculate different profit margins (now correctly as sell - buy)
                buy_order_to_sell_order_margin = best_sell_price - best_buy_price
                buy_order_to_quick_sell_margin = quick_sell - best_buy_price
                quick_buy_to_sell_order_margin = best_sell_price - quick_buy
                
                # Calculate percentage profits
                if best_buy_price > 0:
                    buy_sell_order_percent = (buy_order_to_sell_order_margin / best_buy_price) * 100
                else:
                    buy_sell_order_percent = 0
                
                if quick_buy > 0:
                    quick_buy_sell_percent = (quick_buy_to_sell_order_margin / quick_buy) * 100
                else:
                    quick_buy_sell_percent = 0
                
                # Store result with all relevant data
                result = {
                    'item_id': item_id,
                    'best_buy_price': best_buy_price,
                    'best_sell_price': best_sell_price,
                    'quick_buy': quick_buy,
                    'quick_sell': quick_sell,
                    
                    # Raw profit margins
                    'buy_order_to_sell_order_margin': buy_order_to_sell_order_margin,
                    'buy_order_to_quick_sell_margin': buy_order_to_quick_sell_margin,
                    'quick_buy_to_sell_order_margin': quick_buy_to_sell_order_margin,
                    
                    # Percentage profits
                    'buy_sell_order_percent': buy_sell_order_percent,
                    'quick_buy_sell_percent': quick_buy_sell_percent,
                    
                    # Additional volume data if available
                    'buy_volume': quick_status.get('buyVolume', 0),
                    'sell_volume': quick_status.get('sellVolume', 0)
                }
                
                results.append(result)
                processed_count += 1
            except Exception as e:
                print(f"Error processing item {item_id}: {e}")
                error_count += 1
        
        self.profit_opportunities = results
        print(f"Calculated profit margins for {processed_count} items (with {error_count} errors)")
    
    def get_best_profit_items(self, method='buy_sell_order_percent', min_volume=1000, top_n=20, min_price=0):
        """
        Get the top items with the best profit margins
        
        Parameters:
        - method: The profit calculation method to use for ranking
        - min_volume: Minimum buy/sell volume to consider
        - top_n: Number of top items to return
        - min_price: Minimum buy price to consider (to filter out very cheap items)
        """
        if not self.profit_opportunities:
            print("No profit data available. Calculate profit margins first.")
            return []
        
        # Filter by minimum volume and price
        filtered_items = [
            item for item in self.profit_opportunities 
            if (item['buy_volume'] >= min_volume or item['sell_volume'] >= min_volume) and
               item['best_buy_price'] >= min_price and
               item[method] > 0  # Only include positive margins
        ]
        
        print(f"Found {len(filtered_items)} items meeting volume/price criteria")
        
        # Sort by the specified profit method
        sorted_items = sorted(
            filtered_items, 
            key=lambda x: x[method], 
            reverse=True
        )
        
        # Return the top N items
        return sorted_items[:top_n]
    
    def display_profit_opportunities(self, items, method='buy_sell_order_percent'):
        """
        Display profit opportunities in a readable format
        """
        if not items:
            print("No profit opportunities to display.")
            return
        
        print("\n===== TOP PROFIT OPPORTUNITIES =====")
        
        # Adjust header based on profit method
        if 'percent' in method:
            value_header = 'Profit %'
            value_format = '{:<10.2f}%'
        else:
            value_header = 'Margin (coins)'
            value_format = '{:<15.2f}'
        
        header = f"{'Item ID':<25} {'Buy Price':<12} {'Sell Price':<12} {value_header:<15} {'Volume':<10}"
        print(header)
        print("-" * len(header))
        
        for item in items:
            value = item[method]
            
            print(f"{item['item_id']:<25} "
                  f"{item['best_buy_price']:<12.2f} "
                  f"{item['best_sell_price']:<12.2f} "
                  f"{value_format.format(value)} "
                  f"{max(item['buy_volume'], item['sell_volume']):<10}")
    
    def save_results(self, items, filename=None):
        """
        Save the profit analysis results to a file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'bazaar_profit_analysis_{timestamp}.json'
        
        try:
            with open(filename, 'w') as f:
                json.dump(items, f, indent=2)
            print(f"Saved profit analysis to {filename}")
            
            # Also save a CSV version for easy spreadsheet import
            csv_filename = filename.replace('.json', '.csv')
            with open(csv_filename, 'w') as f:
                # Write header
                header = ["item_id", "buy_price", "sell_price", "margin", "profit_percent", "buy_volume", "sell_volume"]
                f.write(','.join(header) + '\n')
                
                # Write data
                for item in items:
                    row = [
                        item['item_id'],
                        str(item['best_buy_price']),
                        str(item['best_sell_price']),
                        str(item['buy_order_to_sell_order_margin']),
                        str(item['buy_sell_order_percent']),
                        str(item['buy_volume']),
                        str(item['sell_volume'])
                    ]
                    f.write(','.join(row) + '\n')
                
            print(f"Also saved results as CSV to {csv_filename}")
            
        except Exception as e:
            print(f"Error saving results: {e}")


def main():
    """
    Main function to run the profit analyzer
    """
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Analyze Hypixel Bazaar for profit opportunities')
    parser.add_argument('-v', '--min-volume', type=int, default=1000, 
                        help='Minimum volume to consider (default: 1000)')
    parser.add_argument('-n', '--top-n', type=int, default=20,
                        help='Number of top items to display (default: 20)')
    parser.add_argument('-m', '--method', default='buy_sell_order_percent',
                        choices=['buy_sell_order_percent', 'quick_buy_sell_percent', 
                                'buy_order_to_sell_order_margin', 'quick_buy_to_sell_order_margin'],
                        help='Profit calculation method to use for ranking')
    parser.add_argument('-p', '--min-price', type=float, default=0,
                        help='Minimum buy price to consider (default: 0)')
    parser.add_argument('-f', '--file', help='Load data from a previously saved JSON file')
    args = parser.parse_args()
    
    # Initialize the analyzer
    analyzer = HypixelBazaarAnalyzer()
    
    success = False
    
    # If a file was specified, try to load from it
    if args.file:
        success = analyzer.load_from_file(args.file)
    else:
        # Otherwise try to fetch from APIs
        success = analyzer.fetch_all_apis()
        
        # If we got data, immediately save a copy for future use
        if success:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f'bazaar_raw_data_{timestamp}.json', 'w') as f:
                json.dump(analyzer.bazaar_data, f, indent=2)
            print(f"Saved raw bazaar data to bazaar_raw_data_{timestamp}.json")
    
    if success:
        # If we don't already have profit data (from loading a results file)
        if not analyzer.profit_opportunities:
            # Calculate profit margins
            analyzer.calculate_profit_margins()
        
        # Get and display the best profit opportunities
        best_items = analyzer.get_best_profit_items(
            method=args.method, 
            min_volume=args.min_volume, 
            top_n=args.top_n,
            min_price=args.min_price
        )
        analyzer.display_profit_opportunities(best_items, method=args.method)
        
        # Save the results
        analyzer.save_results(best_items)
    else:
        print("\nAll attempts to get bazaar data failed.")
        print("Options:")
        print("1. Check your internet connection")
        print("2. The Hypixel API might be down - try again later")
        print("3. If you previously saved bazaar data, use the -f option to load it:")
        print("   py banalyze.py -f bazaar_raw_data_YYYYMMDD_HHMMSS.json")


if __name__ == "__main__":
    main()
