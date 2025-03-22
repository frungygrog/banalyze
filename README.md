# BAnalyze. 

## Requirements

- Python 3.6 or higher
- `requests` library: `pip install requests`

## Usage

### Basic Usage

```
py banalyze.py
```

This will run the script with default settings, showing the top 20 items by profit percentage with a minimum volume of 1000.

### Command-Line Options

The script supports several command-line options to customize your analysis:

| Option | Long Form | Description | Default |
|--------|-----------|-------------|---------|
| `-v` | `--min-volume` | Minimum trading volume to consider | 1000 |
| `-n` | `--top-n` | Number of top items to display | 20 |
| `-m` | `--method` | Profit calculation method | `buy_sell_order_percent` |
| `-p` | `--min-price` | Minimum buy price to consider | 0 |
| `-x` | `--max-price` | Maximum buy price to consider | No limit |
| `-f` | `--file` | Load data from a previously saved JSON file | None |

### Profit Calculation Methods

You can choose between four different methods to calculate and rank profit opportunities:

- `buy_sell_order_percent`: Profit percentage between buy and sell orders (default)
- `quick_buy_sell_percent`: Profit percentage between quick buy and sell prices
- `buy_order_to_sell_order_margin`: Raw coin margin between buy and sell orders
- `quick_buy_to_sell_order_margin`: Raw coin margin between quick buy and sell prices

### Examples

#### Find high percentage flips:
```
py banalyze.py -m buy_sell_order_percent
```

#### Find items with high raw profit margins:
```
py banalyze.py -m buy_order_to_sell_order_margin
```

#### Filter by price range (items between 100k and 900k coins):
```
py banalyze.py -p 100000 -x 900000
```

#### Show more items with lower volume requirement:
```
py banalyze.py -v 500 -n 30
```

#### Combination of filters:
```
py banalyze.py -m buy_order_to_sell_order_margin -p 100000 -x 900000 -v 500 -n 30
```

#### Use previously saved data (when API is down):
```
py banalyze.py -f bazaar_raw_data_20250322_123456.json
```

## Output

The script displays a table of the top profitable items in the console, including:
- Item ID
- Buy price (what you pay)
- Sell price (what you receive)
- Profit margin (raw coins or percentage)
- Trading volume

It also saves these results to two files:
- `bazaar_profit_analysis_TIMESTAMP.json`: Complete data in JSON format
- `bazaar_profit_analysis_TIMESTAMP.csv`: Simplified data in CSV format for spreadsheets

## Troubleshooting

If the script fails to fetch data:

1. Check your internet connection
2. The Hypixel API might be down or rate-limited - try again later
3. Use the `-f` option to load previously saved data:
   ```
   py banalyze.py -f bazaar_raw_data_TIMESTAMP.json
   ```
4. Examine `last_bazaar_response.json` to see what data (if any) was returned
