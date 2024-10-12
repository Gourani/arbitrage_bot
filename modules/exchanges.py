import ccxt

exchanges = [
    ccxt.okx(),  
    ccxt.bybit({"options": {"defaultType": "spot"}}),
    ccxt.binance(),
    ccxt.kucoin(),
    ccxt.bitmart(),
    ccxt.gate()
]

def get_exchanges():
    return exchanges
