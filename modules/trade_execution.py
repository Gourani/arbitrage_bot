import time
from modules.exchanges import get_exchanges
from modules.symbols import get_order_sizes, get_symbols
from modules.prices import get_last_prices

def calculate_profit(min_price, max_price, order_size, min_fee, max_fee,withdraw_fee):
    """Calculate profit and profit percentage including optional withdrawal fee """
    price_profit = max_price - min_price
    profit = (price_profit * order_size) - (min_fee + max_fee + withdraw_fee)
    profit_percentage = (profit / (min_price * order_size)) * 100
    return profit, profit_percentage

def execute_trade(symbol, order_size, min_exchange, min_price, max_exchange, max_price, paper_trading,post_processing,unit_profit, slippage_tolerance=0.5):
    """Handle the execution of buy, transfer, and sell, accounting for slippage."""
    
    def is_slippage_acceptable(expected_price, actual_price):
        """Check if the slippage is within tolerance."""
        slippage = abs((actual_price - expected_price) / expected_price) * 100
        return slippage <= slippage_tolerance

    if not paper_trading:
        # Step 1: Fetch current market price and compare with min_price
        ticker = min_exchange.fetch_ticker(symbol)
        current_min_price = ticker['ask']  # Buy at ask price

        if not is_slippage_acceptable(min_price, current_min_price):
            print(f"Slippage too high on buy order: Expected {min_price}, Got {current_min_price}")
            return

        # Execute the buy order if slippage is acceptable
        min_exchange.create_limit_buy_order(symbol, order_size, current_min_price)
        print(f"Bought {symbol} on {min_exchange.id} at {current_min_price}")

        # Step 2: Transfer the asset to max_exchange
        withdraw_address = max_exchange.fetch_deposit_address(symbol)
        withdraw_tx = min_exchange.withdraw(symbol, order_size, withdraw_address['address'])
        print(f"Transferred {symbol} from {min_exchange.id} to {max_exchange.id}. Transaction: {withdraw_tx}")

        # Wait for the transfer to complete
        while True:
            balance = max_exchange.fetch_balance()
            if balance[symbol]['free'] >= order_size:
                break
            print(f"Waiting for {symbol} to arrive on {max_exchange.id}...")

        # Step 3: Fetch current sell price and compare with max_price
        ticker = max_exchange.fetch_ticker(symbol)
        current_max_price = ticker['bid']  # Sell at bid price

        if not is_slippage_acceptable(max_price, current_max_price):
            print(f"Slippage too high on sell order: Expected {max_price}, Got {current_max_price}")
            return

        # Execute the sell order if slippage is acceptable
        sell_max = max_exchange.create_limit_sell_order(symbol, order_size, current_max_price)
        print(f"Sold {symbol} on {max_exchange.id} at {current_max_price}")

        # Optional: Post-processing step to transfer profit back
        handle_post_trade(min_exchange, max_exchange, sell_max, order_size,unit_profit, post_processing)

    else:
        print("Paper trading mode. No real transactions executed.")


def handle_post_trade(min_exchange, max_exchange, sell_max, order_size,unit_profit='USDT',post_processing = False):
    """Optionally transfer profit back to the min_exchange for future trades."""
    if post_processing:
        profit_amount = sell_max['info']['executedQty'] * max_exchange.fetch_ticker(order_size)['last']
        withdraw_address_min = min_exchange.fetch_deposit_address(unit_profit)  # Assuming profit is in USDT
        max_exchange.withdraw(unit_profit, profit_amount, withdraw_address_min['address'])
        print(f"Transferred profit from {max_exchange.id} back to {min_exchange.id}")

def find_best_arbitrage(symbol, exchanges, prices, order_size):
    """Find the best exchanges to perform arbitrage."""
    symbol_prices = [exchange_prices.get(symbol, {}).get('last', float('inf')) for exchange_prices in prices]
    min_price, max_price = min(symbol_prices), max(symbol_prices)
    min_exchange, max_exchange = exchanges[symbol_prices.index(min_price)], exchanges[symbol_prices.index(max_price)]
    
    return min_price, max_price, min_exchange, max_exchange

def calculate_fees(exchange, price, order_size):
    """Calculate trading fees for an exchange."""
    fee_rate = exchange.fees['trading']['taker']
    return order_size * price * fee_rate

def bot(paper_trading,withdraw_fee,post_processing,slippage_tolerance, unit_profit, profit_percentage_m, loss_percentage):
    exchanges = get_exchanges()
    symbols = get_symbols()
    order_sizes = get_order_sizes()
    prices = get_last_prices()

    for symbol in symbols:
        ms = int(time.time() * 1000)
        order_size = order_sizes[symbol]
        
        min_price, max_price, min_exchange, max_exchange = find_best_arbitrage(symbol, exchanges, prices, order_size)

        min_fee = calculate_fees(min_exchange, min_price, order_size)
        max_fee = calculate_fees(max_exchange, max_price, order_size)

        profit, profit_percentage = calculate_profit(min_price, max_price, order_size, min_fee, max_fee,withdraw_fee)

        if profit_percentage >= profit_percentage_m:
            print(f"{ms} {symbol} profit: {profit}. Buy {min_exchange.id} at {min_price}, Sell {max_exchange.id} at {max_price}")
            execute_trade(symbol, order_size, min_exchange, min_price, max_exchange, max_price, paper_trading,post_processing,unit_profit,slippage_tolerance)
        elif profit_percentage <= -loss_percentage:
            print(f"{symbol} potential loss exceeds 10%. Skipping trade. Profit percentage: {profit_percentage}%")
        else:
            print(f"{ms} {symbol} no profitable arbitrage opportunity. Profit percentage: {profit_percentage}%")
