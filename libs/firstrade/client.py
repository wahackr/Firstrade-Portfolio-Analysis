import os
import sys
import pandas as pd
from dotenv import load_dotenv
from firstrade import account, symbols

# Load environment variables
load_dotenv()

def get_credentials():
    """Retrieve credentials from environment variables."""
    username = os.getenv("FT_USERNAME")
    password = os.getenv("FT_PASSWORD")
    email = os.getenv("FT_EMAIL")
    
    if not all([username, password, email]):
        print("Error: Missing credentials. Please set FT_USERNAME, FT_PASSWORD, and FT_EMAIL in .env file.")
        sys.exit(1)
    return username, password, email

def login(username, password, email):
    """Authenticate with Firstrade."""
    print("Logging in...")
    ft_ss = account.FTSession(username=username, password=password, email=email, profile_path=".")
    need_code = ft_ss.login()
    if need_code:
        code = input("Please enter the 2FA code sent to your email/phone: ")
        ft_ss.login_two(code)
    return ft_ss

def fetch_portfolio_data(ft_ss):
    """Fetch positions and account data."""
    print("Fetching account data...")
    ft_accounts = account.FTAccountData(ft_ss)
    if len(ft_accounts.account_numbers) < 1:
        print("No accounts found.")
        sys.exit(1)
        
    account_number = ft_accounts.account_numbers[0]
    print(f"Using account: {account_number}")
    
    print("Fetching positions...")
    positions = ft_accounts.get_positions(account=account_number)
    
    data = []
    for item in positions["items"]:
        symbol = item["symbol"]
        quantity = float(item["quantity"])
        
        try:
            quote = symbols.SymbolQuote(ft_ss, account_number, symbol)
            current_price = float(quote.last)
            change_percent = float(quote.change.replace('%', '')) if isinstance(quote.change, str) else float(quote.change)
            # Calculate market value based on latest price to be consistent
            market_value = quantity * current_price
            
            # Calculate Day Change ($)
            # Current Value = Previous Value * (1 + Change%)
            # Previous Value = Current Value / (1 + Change%)
            # Day Change = Current Value - Previous Value
            if change_percent == -100:
                day_change = -market_value
            else:
                previous_value = market_value / (1 + change_percent / 100)
                day_change = market_value - previous_value

            # Format Label
            # Symbol (Bold)
            # Change %
            # Day Change $ (with sign)
            label = f"<b>{symbol}</b><br>{change_percent:.2f}%<br>{day_change:+.2f}"

            data.append({
                "Symbol": symbol,
                "Market Value": market_value,
                "Change %": change_percent,
                "Day Change": day_change,
                "Quantity": quantity,
                "Price": current_price,
                "Label": label
            })
            print(f"Processed {symbol}: Value=${market_value:.2f}, Change={change_percent}%, DayChange=${day_change:.2f}")
        except Exception as e:
            print(f"Failed to fetch data for {symbol}: {e}")
    
    return pd.DataFrame(data)
