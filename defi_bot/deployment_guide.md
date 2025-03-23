# DeFi Productivity Bot - Deployment Guide

## Prerequisites

1. **Telegram Bot Token**
   - Create a new bot through BotFather on Telegram
   - Save the provided token for configuration

2. **Google Calendar API Credentials**
   - Go to the Google Cloud Console
   - Create a new project
   - Enable the Google Calendar API
   - Create OAuth 2.0 credentials
   - Download the credentials JSON file

3. **Etherscan API Key (Optional but Recommended)**
   - Register on Etherscan.io
   - Create an API key from your account dashboard

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/defi-productivity-bot.git
   cd defi-productivity-bot
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   - Copy the example environment file
     ```bash
     cp .env.example .env
     ```
   - Edit the `.env` file with your credentials:
     ```
     TELEGRAM_TOKEN=your_telegram_bot_token
     ETH_RPC_URL=your_ethereum_rpc_url
     ETHERSCAN_API_KEY=your_etherscan_api_key
     GOOGLE_CLIENT_ID=your_google_client_id
     GOOGLE_CLIENT_SECRET=your_google_client_secret
     GOOGLE_REFRESH_TOKEN=your_google_refresh_token
     DATABASE_PATH=defi_bot.db
     ```

4. **Initialize the Database**
   ```bash
   python database.py
   ```

5. **Set Up Google Calendar Authentication**
   - For the first run, you'll need to authenticate with Google:
     ```bash
     python calendar_integration.py
     ```
   - Follow the prompts to authorize the application
   - This will create a `token.json` file for future authentication

## Running the Bot

1. **Start the Bot**
   ```bash
   python main.py
   ```

2. **Verify the Bot is Running**
   - Open Telegram
   - Search for your bot by username
   - Send the `/start` command
   - You should receive a welcome message

## Deployment Options

### Local Deployment

- The setup above will run the bot on your local machine
- Ensure your machine stays on for the bot to function continuously

### Cloud Deployment (Recommended)

#### Option 1: PythonAnywhere (Free Tier)
1. Sign up for a PythonAnywhere account
2. Upload the project files
3. Install dependencies using the PythonAnywhere console
4. Set up a scheduled task to run `main.py`

#### Option 2: Heroku (Free Tier)
1. Create a `Procfile` with the content:
   ```
   worker: python main.py
   ```
2. Create a Heroku app and push your code
3. Set the environment variables in the Heroku dashboard
4. Start the worker dyno

#### Option 3: Replit (Free Tier)
1. Create a new Replit project
2. Upload the project files
3. Set the environment variables in the Secrets tab
4. Set the run command to `python main.py`
5. Use UptimeRobot to keep the Replit project active

## Usage Guide

### Basic Commands

- `/start` - Start the bot and see welcome message
- `/help` - Show help message with all available commands
- `/add_wallet [address]` - Add a wallet for monitoring
- `/add_position` - Add a new DeFi position
- `/portfolio` - View your current DeFi positions
- `/gas` - Check current gas prices and optimal transaction times
- `/security [contract_address]` - Verify contract safety
- `/yields` - View available yield opportunities
- `/upcoming_claims` - View upcoming yield claims
- `/sync_calendar` - Sync all positions with Google Calendar

### Workflow Examples

1. **Adding a New DeFi Position**
   - Use `/add_position`
   - Select the protocol
   - Enter the amount and asset
   - Confirm the details
   - The position will be added and a calendar event created

2. **Checking Gas Prices Before a Transaction**
   - Use `/gas`
   - Review current gas prices
   - Follow the recommendation for optimal transaction time

3. **Verifying a Contract Before Interacting**
   - Use `/security [contract_address]`
   - Review the security assessment
   - Make an informed decision based on the risk score

## Troubleshooting

### Common Issues

1. **Bot Not Responding**
   - Check if the bot is running
   - Verify your Telegram token is correct
   - Ensure your internet connection is stable

2. **Calendar Events Not Creating**
   - Check your Google API credentials
   - Verify the token.json file exists
   - Try running `/sync_calendar` to force a sync

3. **Gas Price Information Not Updating**
   - Check your Etherscan API key
   - Verify your Ethereum RPC URL is working
   - The free tier may have rate limits

### Getting Help

If you encounter issues not covered here, please:
1. Check the logs for error messages
2. Consult the Telegram Bot API documentation
3. Review the Google Calendar API documentation

## Customization

### Adding New Features

The modular design allows for easy extension:

1. **New Bot Commands**
   - Add new command handlers in `bot.py`
   - Register them in the main function

2. **Additional DeFi Protocols**
   - Extend the protocol list in the YieldSense class
   - Update the yield data retrieval functions

3. **Custom Notifications**
   - Add new notification types in the scheduler
   - Create corresponding handlers in the bot

## Maintenance

### Regular Updates

To keep the bot running smoothly:

1. **Update Dependencies**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

2. **Check for API Changes**
   - Telegram Bot API
   - Google Calendar API
   - Etherscan API

3. **Database Maintenance**
   - Periodically backup the SQLite database
   - Clean up old records if the database grows too large
