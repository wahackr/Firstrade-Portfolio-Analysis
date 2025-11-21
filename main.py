from libs.firstrade.client import get_credentials, login, fetch_portfolio_data
from libs.visualization import generate_market_map

def main():
    username, password, email, mfa_secret = get_credentials()
    ft_ss = login(username, password, email, mfa_secret)
    df = fetch_portfolio_data(ft_ss)
    generate_market_map(df)

if __name__ == "__main__":
    main()
