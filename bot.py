from logging.handlers import TimedRotatingFileHandler
import time
import argparse
from modules.trade_execution import bot
import logging
import os

# Create log directory
log_directory = 'logs'

if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Configure logging
log_filename = time.strftime("%Y-%m-%d_%H-%M-%S") + "_arbitrage_bot.log"
log_file_path = os.path.join(log_directory, log_filename)
handler = TimedRotatingFileHandler(log_filename, when="H", interval=1, backupCount=0)

logging.basicConfig(
    handlers=[handler],
    filename=log_file_path,
    level=logging.INFO,  # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s'
)



wait_time = 5

def main(paper_trading, withdraw_fee, post_processing, slippage_tolerance, unit_profit, profit_percentage, loss_percentage):
   # print(f"Starting bot with paper_trading={paper_trading}, withdraw_fee={withdraw_fee}, post_processing={post_processing}, slippage_tolerance={slippage_tolerance}, unit_profit={unit_profit}, profit_percentage={profit_percentage}, loss_percentage={loss_percentage}")
    logging.info(f"Starting bot with paper_trading={paper_trading}, withdraw_fee={withdraw_fee}, post_processing={post_processing}, slippage_tolerance={slippage_tolerance}, unit_profit={unit_profit}, profit_percentage={profit_percentage}, loss_percentage={loss_percentage}")

    while True:
        try:
            bot(paper_trading=paper_trading, withdraw_fee=withdraw_fee, post_processing=post_processing, slippage_tolerance=slippage_tolerance, unit_profit=unit_profit, profit_percentage_m=profit_percentage, loss_percentage=loss_percentage)
        except Exception as e:
          #  print("Exception: ", e)
            logging.exception("Exception occurred: %s", e)
        time.sleep(wait_time)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the bot")
    
    # Paper trading argument
    parser.add_argument('--paper_trading', type=str, default="true", 
                        help="Set to 'false' to disable paper trading (default is 'true')")
    
    # Withdraw fee argument, default to 0 if not provided
    parser.add_argument('--withdraw_fee', type=float, default=0, 
                        help="Optional withdrawal fee (default is 0)")
    
    # Post-processing argument, default to False
    parser.add_argument('--post_processing', type=str, default="false", 
                        help="Set to 'true' to enable post-processing (default is 'false')")
    
    # Slippage threshold argument, default to 0.5
    parser.add_argument('--slippage_tolerance', type=float, default=0.5, 
                        help="Maximum allowable slippage percentage (default is 0.5)")
    
    # Unit profit argument, default to 'USDT'
    parser.add_argument('--unit_profit', type=str, default="USDT", 
                        help="Unit for profit calculation (default is 'USDT')")
    
    # Profit percentage argument, default to 0
    parser.add_argument('--profit_percentage', type=float, default=50, 
                        help="Target profit percentage (default is 0)")

    # Loss percentage argument, default to 0
    parser.add_argument('--loss_percentage', type=float, default=10, 
                        help="Stop-loss percentage (default is 0)")
    
    args = parser.parse_args()

    # Convert the string arguments to booleans
    paper_trading = args.paper_trading.lower() == 'true'
    post_processing = args.post_processing.lower() == 'true'
    
    main(paper_trading, args.withdraw_fee, post_processing, args.slippage_tolerance, args.unit_profit, args.profit_percentage, args.loss_percentage)
