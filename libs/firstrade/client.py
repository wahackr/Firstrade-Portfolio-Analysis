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
    mfa_secret = os.getenv("FT_MFA_SECRET")  # Optional MFA secret for TOTP
    
    if not all([username, password]):
        print("Error: Missing credentials. Please set FT_USERNAME and FT_PASSWORD in .env file.")
        sys.exit(1)
    return username, password, email, mfa_secret

def login(username, password, email, mfa_secret=None):
    """Authenticate with Firstrade."""
    print("Logging in...")
    ft_ss = account.FTSession(
        username=username, 
        password=password, 
        email=email, 
        #mfa_secret=mfa_secret,        
        profile_path="."
    )
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
            
            # quote.change is the dollar price change, not percentage
            price_change = float(quote.change) if quote.change else 0.0
            
            # Calculate market value based on latest price
            market_value = quantity * current_price
            
            # Calculate day change in dollars for the position
            day_change = quantity * price_change
            
            # Calculate percentage change
            if current_price > 0:
                previous_price = current_price - price_change
                change_percent = (price_change / previous_price * 100) if previous_price != 0 else 0.0
            else:
                change_percent = 0.0

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
            print(f"Processed {symbol}: Value=${market_value:.2f}, Change={change_percent:.2f}%, DayChange=${day_change:.2f}")
        except Exception as e:
            print(f"Failed to fetch data for {symbol}: {e}")
    
    return pd.DataFrame(data)
