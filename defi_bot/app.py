import os
import logging
from flask import Flask, request, jsonify
from threading import Thread
import database
import bot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def index():
    """Home page route."""
    return "DeFi Productivity Bot Server is running!"

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint for Telegram updates."""
    # This would be used in production for webhook mode
    # For this demo, we'll use polling mode
    return jsonify({"status": "success"})

def run_flask():
    """Run the Flask app in a separate thread."""
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

def main():
    """Main function to start the application."""
    # Initialize the database
    db_path = os.getenv('DATABASE_PATH', 'defi_bot.db')
    database.initialize_database(db_path)
    logger.info(f"Database initialized at {db_path}")
    
    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    logger.info("Flask server started")
    
    # Start the Telegram bot
    logger.info("Starting Telegram bot")
    bot.main()

if __name__ == '__main__':
    main()
