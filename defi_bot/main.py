import os
import logging
from dotenv import load_dotenv
import database
import bot
import scheduler
from defi_core import DeFiGuard, GasWizard, YieldSense

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Main function to start the application."""
    logger.info("Starting DeFi Productivity App")
    
    # Initialize the database
    db_path = os.getenv('DATABASE_PATH', 'defi_bot.db')
    database.initialize_database(db_path)
    logger.info(f"Database initialized at {db_path}")
    
    # Initialize core components
    defi_guard = DeFiGuard()
    gas_wizard = GasWizard()
    yield_sense = YieldSense()
    logger.info("Core components initialized")
    
    # Start the background scheduler
    background_scheduler = scheduler.start_scheduler()
    logger.info("Background scheduler started")
    
    # Start the Telegram bot
    logger.info("Starting Telegram bot")
    bot.main()
    
    # This point is reached when the bot is stopped
    background_scheduler.shutdown()
    logger.info("Application shutdown complete")

if __name__ == '__main__':
    main()
