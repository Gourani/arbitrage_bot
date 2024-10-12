from modules.exchanges import get_exchanges
from modules.symbols import get_symbols

def get_last_prices():
    exchanges = get_exchanges()
    symbols = get_symbols()
    prices = []
    for exchange in exchanges:
        try:
            exchange.load_markets()
            ticker_data = exchange.fetch_tickers(symbols)
            prices.append(ticker_data)
        except Exception as e:
            print(f"Error fetching prices from {exchange.id}: {e}")
            prices.append({})
    return prices
