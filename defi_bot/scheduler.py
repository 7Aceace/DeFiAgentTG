import os
import logging
import sqlite3
from sqlite3 import Error
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import blockchain_utils
import calendar_integration

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def create_connection(db_file):
    """Create a database connection to the SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        logger.error(f"Database connection error: {e}")
    
    return conn

def check_gas_prices_and_notify():
    """Check gas prices and notify users if they are low."""
    logger.info("Checking gas prices...")
    
    # Get current gas prices
    gas_prices = blockchain_utils.get_gas_prices()
    
    # Define threshold for "low" gas prices (adjust as needed)
    LOW_GAS_THRESHOLD = 30
    
    if gas_prices['average'] <= LOW_GAS_THRESHOLD:
        # Get users with active alerts for gas prices
        db_path = os.getenv('DATABASE_PATH', 'defi_bot.db')
        conn = create_connection(db_path)
        
        if not conn:
            logger.error("Failed to connect to database")
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT u.telegram_id
                FROM alerts a
                JOIN users u ON a.user_id = u.id
                WHERE a.alert_type = 'gas' AND a.is_active = 1
                """
            )
            users = cursor.fetchall()
            
            # In a real implementation, this would send Telegram messages to users
            # For this demo, we'll just log the notifications
            for user in users:
                telegram_id = user[0]
                logger.info(f"Would notify user {telegram_id} about low gas prices: {gas_prices['average']} Gwei")
        except Error as e:
            logger.error(f"Database error: {e}")
        finally:
            conn.close()

def check_upcoming_yield_claims():
    """Check for upcoming yield claims and notify users."""
    logger.info("Checking upcoming yield claims...")
    
    db_path = os.getenv('DATABASE_PATH', 'defi_bot.db')
    conn = create_connection(db_path)
    
    if not conn:
        logger.error("Failed to connect to database")
        return
    
    try:
        cursor = conn.cursor()
        
        # Get all users
        cursor.execute("SELECT id, telegram_id FROM users")
        users = cursor.fetchall()
        
        for user in users:
            db_user_id, telegram_id = user
            
            # Get upcoming claims in the next 24 hours
            upcoming_claims = calendar_integration.get_upcoming_yield_claims_for_user(db_user_id, 1)
            
            for claim in upcoming_claims:
                # In a real implementation, this would send Telegram messages to users
                # For this demo, we'll just log the notifications
                logger.info(
                    f"Would notify user {telegram_id} about upcoming yield claim: "
                    f"{claim['protocol']} {claim['asset']} on {claim['claim_date']}"
                )
    except Error as e:
        logger.error(f"Database error: {e}")
    finally:
        conn.close()

def check_security_alerts():
    """Check for security alerts and notify users."""
    logger.info("Checking security alerts...")
    
    # In a real implementation, this would check for security incidents
    # For this demo, we'll just log the check
    
    # Example of what this would do:
    # 1. Check for recent exploits or hacks
    # 2. Check for contract vulnerabilities
    # 3. Check for suspicious transactions
    
    # If any issues are found, notify affected users
    
    logger.info("Security check completed, no issues found")

def start_scheduler():
    """Start the background scheduler for periodic tasks."""
    scheduler = BackgroundScheduler()
    
    # Check gas prices every hour
    scheduler.add_job(check_gas_prices_and_notify, 'interval', hours=1)
    
    # Check upcoming yield claims every day at 9 AM
    scheduler.add_job(
        check_upcoming_yield_claims,
        'cron',
        hour=9,
        minute=0
    )
    
    # Check security alerts every 6 hours
    scheduler.add_job(check_security_alerts, 'interval', hours=6)
    
    # Start the scheduler
    scheduler.start()
    logger.info("Background scheduler started")
    
    return scheduler

if __name__ == '__main__':
    # Test the functions
    check_gas_prices_and_notify()
    check_upcoming_yield_claims()
    check_security_alerts()
