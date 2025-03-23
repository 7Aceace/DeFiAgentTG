import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler,
    CallbackQueryHandler,
)
from dotenv import load_dotenv
import database
import blockchain_utils
import calendar_integration

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
WALLET_ADDRESS, PROTOCOL_SELECTION, AMOUNT_INPUT, CONFIRMATION = range(4)

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    
    # Store user in database if not exists
    db_path = os.getenv('DATABASE_PATH', 'defi_bot.db')
    conn = database.create_connection(db_path)
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR IGNORE INTO users (telegram_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
                """,
                (user.id, user.username, user.first_name, user.last_name)
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Database error: {e}")
        finally:
            conn.close()
    
    update.message.reply_text(
        f'Hi {user.first_name}! I am your DeFi productivity assistant. '
        f'I combine features from DeFiGuard, GasWizard, and YieldSense to help you manage your DeFi activities.\n\n'
        f'Here are some commands you can use:\n'
        f'/add_wallet - Add a wallet for monitoring\n'
        f'/add_position - Add a new DeFi position\n'
        f'/portfolio - View your current DeFi positions\n'
        f'/gas - Check current gas prices\n'
        f'/security - Verify contract safety\n'
        f'/yields - View available yield opportunities\n'
        f'/upcoming_claims - View upcoming yield claims\n'
        f'/help - Get more information about available commands'
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        'Here are all available commands:\n\n'
        '/start - Start the bot and see welcome message\n'
        '/add_wallet [address] - Add a wallet for monitoring\n'
        '/add_position - Add a new DeFi position\n'
        '/portfolio - View your current DeFi positions\n'
        '/gas - Check current gas prices and optimal transaction times\n'
        '/security [contract_address] - Verify contract safety\n'
        '/yields - View available yield opportunities\n'
        '/claim [protocol] - Information about claiming yields\n'
        '/upcoming_claims - View upcoming yield claims\n'
        '/sync_calendar - Sync all positions with Google Calendar\n'
        '/alert [type] [parameters] - Set up custom alerts\n'
        '/help - Show this help message'
    )

def add_wallet_start(update: Update, context: CallbackContext) -> int:
    """Start the wallet addition conversation."""
    update.message.reply_text(
        'Please send me your Ethereum wallet address to start monitoring.'
    )
    return WALLET_ADDRESS

def wallet_address_received(update: Update, context: CallbackContext) -> int:
    """Process the wallet address."""
    wallet_address = update.message.text
    user_id = update.effective_user.id
    
    # Basic validation (this would be more robust in production)
    if wallet_address.startswith('0x') and len(wallet_address) == 42:
        # Store in database
        db_path = os.getenv('DATABASE_PATH', 'defi_bot.db')
        conn = database.create_connection(db_path)
        if conn:
            try:
                # Get user_id from telegram_id
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (user_id,))
                user_row = cursor.fetchone()
                
                if user_row:
                    db_user_id = user_row[0]
                    
                    # Insert wallet
                    cursor.execute(
                        """
                        INSERT INTO wallets (user_id, address, label)
                        VALUES (?, ?, ?)
                        """,
                        (db_user_id, wallet_address, f"Wallet added on {datetime.now().strftime('%Y-%m-%d')}")
                    )
                    conn.commit()
                    
                    update.message.reply_text(
                        f'Great! I\'ve added wallet {wallet_address} for monitoring.\n\n'
                        f'I\'ll now track your DeFi positions and alert you about important events.'
                    )
                else:
                    update.message.reply_text(
                        'Error: User not found in database. Please try /start first.'
                    )
            except Exception as e:
                logger.error(f"Database error: {e}")
                update.message.reply_text(
                    'Sorry, there was an error adding your wallet. Please try again later.'
                )
            finally:
                conn.close()
        else:
            update.message.reply_text(
                'Sorry, there was an error connecting to the database. Please try again later.'
            )
        
        return ConversationHandler.END
    else:
        update.message.reply_text(
            'That doesn\'t look like a valid Ethereum address. '
            'Please send a valid address starting with 0x and containing 42 characters.'
        )
        return WALLET_ADDRESS

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel the conversation."""
    update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END

def check_gas(update: Update, context: CallbackContext) -> None:
    """Check current gas prices."""
    # Get real-time gas prices
    gas_prices = blockchain_utils.get_gas_prices()
    
    # Estimate costs for a standard transaction
    slow_cost = blockchain_utils.estimate_transaction_cost(21000, gas_prices['slow'])
    avg_cost = blockchain_utils.estimate_transaction_cost(21000, gas_prices['average'])
    fast_cost = blockchain_utils.estimate_transaction_cost(21000, gas_prices['fast'])
    
    update.message.reply_text(
        f'Current Ethereum Gas Prices (Gwei):\n\n'
        f'🐢 Slow: {gas_prices["slow"]} - Est. time: ~10 mins\n'
        f'   Cost: {slow_cost["eth"]:.6f} ETH (${slow_cost["usd"]:.2f})\n\n'
        f'🚶 Average: {gas_prices["average"]} - Est. time: ~3 mins\n'
        f'   Cost: {avg_cost["eth"]:.6f} ETH (${avg_cost["usd"]:.2f})\n\n'
        f'🏎️ Fast: {gas_prices["fast"]} - Est. time: ~30 secs\n'
        f'   Cost: {fast_cost["eth"]:.6f} ETH (${fast_cost["usd"]:.2f})\n\n'
        f'Recommendation: Best time to transact is typically on weekends or between 1-5 AM UTC.'
    )

def check_security(update: Update, context: CallbackContext) -> None:
    """Check contract security."""
    args = context.args
    
    if not args:
        update.message.reply_text(
            'Please provide a contract address to check.\n'
            'Example: /security 0x1234...'
        )
        return
    
    contract_address = args[0]
    
    # Check contract security
    security = blockchain_utils.check_contract_security(contract_address)
    
    if not security.get('valid', False):
        update.message.reply_text(
            f'Error: {security.get("message", "Invalid contract address")}'
        )
        return
    
    # Format the response
    risk_score = security.get('risk_score', 5)
    risk_emoji = '🔴' if risk_score > 7 else '🟠' if risk_score > 4 else '🟢'
    
    issues = security.get('issues', [])
    issues_text = '\n'.join([f'• {issue}' for issue in issues]) if issues else 'No specific issues detected'
    
    update.message.reply_text(
        f'Security Check for {contract_address}:\n\n'
        f'{risk_emoji} Risk Score: {risk_score}/10\n\n'
        f'✅ Verified: {security.get("verified", False)}\n'
        f'⏱️ Age: {security.get("age_days", 0)} days\n'
        f'👥 Used by: {security.get("usage", {}).get("unique_addresses", 0)} addresses\n\n'
        f'Issues:\n{issues_text}\n\n'
        f'Always do your own research before interacting with any smart contract.'
    )

def view_portfolio(update: Update, context: CallbackContext) -> None:
    """View current DeFi positions."""
    user_id = update.effective_user.id
    
    # Get user's positions from database
    db_path = os.getenv('DATABASE_PATH', 'defi_bot.db')
    conn = database.create_connection(db_path)
    
    if not conn:
        update.message.reply_text(
            'Sorry, there was an error connecting to the database. Please try again later.'
        )
        return
    
    try:
        # Get user_id from telegram_id
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (user_id,))
        user_row = cursor.fetchone()
        
        if not user_row:
            update.message.reply_text(
                'Error: User not found in database. Please try /start first.'
            )
            return
        
        db_user_id = user_row[0]
        
        # Get positions
        cursor.execute(
            """
            SELECT protocol, asset, amount, position_type, apy
            FROM positions
            WHERE user_id = ? AND status = 'active'
            """,
            (db_user_id,)
        )
        positions = cursor.fetchall()
        
        if not positions:
            update.message.reply_text(
                'You don\'t have any active DeFi positions yet.\n'
                'Use /add_position to add a new position.'
            )
            return
        
        # Format the response
        position_text = ''
        total_value_usd = 0
        total_daily_yield_usd = 0
        
        for i, position in enumerate(positions):
            protocol, asset, amount, position_type, apy = position
            
            # In a real implementation, this would calculate actual USD values
            # For this demo, we'll use mock values
            value_usd = float(amount) * 100  # Mock conversion
            daily_yield_usd = value_usd * (float(apy or 0) / 100 / 365)
            
            total_value_usd += value_usd
            total_daily_yield_usd += daily_yield_usd
            
            position_text += f"{i+1}. {protocol}: {amount} {asset} {position_type} ({apy}% APY)\n"
        
        # Get upcoming claims
        upcoming_claims = calendar_integration.get_upcoming_yield_claims_for_user(db_user_id)
        upcoming_text = ''
        
        if upcoming_claims:
            next_claim = min(upcoming_claims, key=lambda x: x['days_until'])
            upcoming_text = f"Next yield claim: {next_claim['protocol']} {next_claim['asset']} in {next_claim['days_until']} days"
        else:
            upcoming_text = "No upcoming yield claims scheduled"
        
        update.message.reply_text(
            f'Your DeFi Portfolio:\n\n'
            f'{position_text}\n'
            f'Total Value: ~${total_value_usd:.2f}\n'
            f'Estimated Daily Yield: ~${total_daily_yield_usd:.2f}\n\n'
            f'{upcoming_text}'
        )
    except Exception as e:
        logger.error(f"Database error: {e}")
        update.message.reply_text(
            'Sorry, there was an error retrieving your portfolio. Please try again later.'
        )
    finally:
        conn.close()

def view_yields(update: Update, context: CallbackContext) -> None:
    """View available yield opportunities."""
    keyboard = [
        [
            InlineKeyboardButton("Lending", callback_data='yields_lending'),
            InlineKeyboardButton("Liquidity", callback_data='yields_liquidity'),
        ],
        [
            InlineKeyboardButton("Staking", callback_data='yields_staking'),
            InlineKeyboardButton("Farming", callback_data='yields_farming'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Select a yield category to explore:', reply_markup=reply_markup)

def yield_button(update: Update, context: CallbackContext) -> None:
    """Handle yield category button presses."""
    query = update.callback_query
    query.answer()
    
    category = query.data.split('_')[1]
    
    # Get yield opportunities
    yields = blockchain_utils.get_defi_yields()
    
    if category in yields:
        opportunities = yields[category]
        
        text = f'Top {category.capitalize()} Opportunities:\n\n'
        
        for i, opp in enumerate(opportunities):
            text += f"{i+1}. {opp['protocol']} {opp['asset']}: {opp['apy']}% APY\n"
        
        text += '\nWould you like to add any of these to your portfolio? Use /add_position'
    else:
        text = 'Sorry, no opportunities found in this category.'
    
    query.edit_message_text(text=text)

def add_position_start(update: Update, context: CallbackContext) -> int:
    """Start the add position conversation."""
    # Get protocols from blockchain utils
    yields = blockchain_utils.get_defi_yields()
    protocols = set()
    
    for category in yields:
        for opp in yields[category]:
            protocols.add(opp['protocol'])
    
    protocols = sorted(list(protocols))
    context.user_data['protocols'] = protocols
    
    keyboard = []
    row = []
    for i, protocol in enumerate(protocols):
        row.append(InlineKeyboardButton(protocol, callback_data=f'protocol_{protocol}'))
        if (i + 1) % 2 == 0 or i == len(protocols) - 1:
            keyboard.append(row)
            row = []
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Select the protocol where you added a position:', reply_markup=reply_markup)
    return PROTOCOL_SELECTION

def protocol_selected(update: Update, context: CallbackContext) -> int:
    """Handle protocol selection."""
    query = update.callback_query
    query.answer()
    
    protocol = query.data.split('_')[1]
    context.user_data['protocol'] = protocol
    
    query.edit_message_text(
        text=f'You selected {protocol}. Now, please enter the amount and asset (e.g., "100 USDC"):'
    )
    return AMOUNT_INPUT

def amount_received(update: Update, context: CallbackContext) -> int:
    """Process the amount input."""
    input_text = update.message.text
    
    # Parse amount and asset
    parts = input_text.split()
    if len(parts) < 2:
        update.message.reply_text(
            'Please enter both amount and asset (e.g., "100 USDC").'
        )
        return AMOUNT_INPUT
    
    try:
        amount = float(parts[0])
        asset = ' '.join(parts[1:])
        
        context.user_data['amount'] = amount
        context.user_data['asset'] = asset
        
        protocol = context.user_data['protocol']
        
        # Find APY for this protocol and asset
        apy = None
        yields = blockchain_utils.get_defi_yields()
        
        for category in yields:
            for opp in yields[category]:
                if opp['protocol'] == protocol and opp['asset'] == asset:
                    apy = opp['apy']
                    context.user_data['position_type'] = category
                    break
            if apy:
                break
        
        context.user_data['apy'] = apy
        
        update.message.reply_text(
            f'You\'re adding a position of {amount} {asset} in {protocol}'
            f'{f" with estimated APY of {apy}%" if apy else ""}.\n\n'
            f'Is this correct? (Yes/No)'
        )
        return CONFIRMATION
    except ValueError:
        update.message.reply_text(
            'Invalid amount format. Please enter a number followed by the asset name (e.g., "100 USDC").'
        )
        return AMOUNT_INPUT

def confirmation(update: Update, context: CallbackContext) -> int:
    """Handle confirmation of position details."""
    response = update.message.text.lower()
    user_id = update.effective_user.id
    
    if response in ['yes', 'y']:
        protocol = context.user_data['protocol']
        amount = context.user_data['amount']
        asset = context.user_data['asset']
        apy = context.user_data.get('apy')
        position_type = context.user_data.get('position_type', 'supply')
        
        # Get user_id from database
        db_path = os.getenv('DATABASE_PATH', 'defi_bot.db')
        conn = database.create_connection(db_path)
        
        if not conn:
            update.message.reply_text(
                'Sorry, there was an error connecting to the database. Please try again later.'
            )
            return ConversationHandler.END
        
        try:
            # Get user_id from telegram_id
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (user_id,))
            user_row = cursor.fetchone()
            
            if not user_row:
                update.message.reply_text(
                    'Error: User not found in database. Please try /start first.'
                )
                return ConversationHandler.END
            
            db_user_id = user_row[0]
            
            # Add position to database and create calendar event
            success = calendar_integration.setup_calendar_sync_for_new_position(
                db_user_id, protocol, asset, amount, position_type, apy
            )
            
            if success:
                update.message.reply_text(
                    f'Great! I\'ve added your position of {amount} {asset} in {protocol}.\n\n'
                    f'I\'ll monitor this position and notify you about important events.\n'
                    f'A calendar event has been created for the next yield claim opportunity.'
                )
            else:
                update.message.reply_text(
                    f'I\'ve added your position of {amount} {asset} in {protocol}, but there was an error creating the calendar event.\n\n'
                    f'You can try to sync your calendar later with /sync_calendar.'
                )
        except Exception as e:
            logger.error(f"Database error: {e}")
            update.message.reply_text(
                'Sorry, there was an error adding your position. Please try again later.'
            )
        finally:
            conn.close()
        
        return ConversationHandler.END
    else:
        update.message.reply_text('Let\'s try again. Please use /add_position to start over.')
        return ConversationHandler.END

def view_upcoming_claims(update: Update, context: CallbackContext) -> None:
    """View upcoming yield claims."""
    user_id = update.effective_user.id
    
    # Get user_id from database
    db_path = os.getenv('DATABASE_PATH', 'defi_bot.db')
    conn = database.create_connection(db_path)
    
    if not conn:
        update.message.reply_text(
            'Sorry, there was an error connecting to the database. Please try again later.'
        )
        return
    
    try:
        # Get user_id from telegram_id
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (user_id,))
        user_row = cursor.fetchone()
        
        if not user_row:
            update.message.reply_text(
                'Error: User not found in database. Please try /start first.'
            )
            return
        
        db_user_id = user_row[0]
        
        # Get upcoming claims
        upcoming_claims = calendar_integration.get_upcoming_yield_claims_for_user(db_user_id, 30)
        
        if not upcoming_claims:
            update.message.reply_text(
                'You don\'t have any upcoming yield claims in the next 30 days.\n'
                'Use /add_position to add new positions or /sync_calendar to update your calendar.'
            )
            return
        
        # Sort by days until
        upcoming_claims.sort(key=lambda x: x['days_until'])
        
        # Format the response
        text = 'Your Upcoming Yield Claims:\n\n'
        
        for claim in upcoming_claims:
            text += f"• {claim['protocol']} {claim['asset']}: {claim['claim_date']} ({claim['days_until']} days)\n"
        
        text += '\nThese events have been added to your Google Calendar.'
        
        update.message.reply_text(text)
    except Exception as e:
        logger.error(f"Error: {e}")
        update.message.reply_text(
            'Sorry, there was an error retrieving your upcoming claims. Please try again later.'
        )
    finally:
        conn.close()

def sync_calendar(update: Update, context: CallbackContext) -> None:
    """Sync all positions with Google Calendar."""
    user_id = update.effective_user.id
    
    # Get user_id from database
    db_path = os.getenv('DATABASE_PATH', 'defi_bot.db')
    conn = database.create_connection(db_path)
    
    if not conn:
        update.message.reply_text(
            'Sorry, there was an error connecting to the database. Please try again later.'
        )
        return
    
    try:
        # Get user_id from telegram_id
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (user_id,))
        user_row = cursor.fetchone()
        
        if not user_row:
            update.message.reply_text(
                'Error: User not found in database. Please try /start first.'
            )
            return
        
        db_user_id = user_row[0]
        
        # Sync calendar
        success = calendar_integration.sync_all_positions_with_calendar(db_user_id)
        
        if success:
            update.message.reply_text(
                'Successfully synced your positions with Google Calendar.\n'
                'Use /upcoming_claims to view your upcoming yield claims.'
            )
        else:
            update.message.reply_text(
                'There was an error syncing your positions with Google Calendar.\n'
                'Please check your calendar settings and try again later.'
            )
    except Exception as e:
        logger.error(f"Error: {e}")
        update.message.reply_text(
            'Sorry, there was an error syncing your calendar. Please try again later.'
        )
    finally:
        conn.close()

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token
    token = os.getenv('TELEGRAM_TOKEN', 'YOUR_TOKEN_HERE')
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Basic command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("gas", check_gas))
    dispatcher.add_handler(CommandHandler("security", check_security))
    dispatcher.add_handler(CommandHandler("portfolio", view_portfolio))
    dispatcher.add_handler(CommandHandler("yields", view_yields))
    dispatcher.add_handler(CommandHandler("upcoming_claims", view_upcoming_claims))
    dispatcher.add_handler(CommandHandler("sync_calendar", sync_calendar))
    
    # Callback query handler for yield buttons
    dispatcher.add_handler(CallbackQueryHandler(yield_button, pattern='^yields_'))
    
    # Add wallet conversation handler
    add_wallet_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add_wallet', add_wallet_start)],
        states={
            WALLET_ADDRESS: [MessageHandler(Filters.text & ~Filters.command, wallet_address_received)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(add_wallet_conv_handler)
    
    # Add position conversation handler
    add_position_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add_position', add_position_start)],
        states={
            PROTOCOL_SELECTION: [CallbackQueryHandler(protocol_selected, pattern='^protocol_')],
            AMOUNT_INPUT: [MessageHandler(Filters.text & ~Filters.command, amount_received)],
            CONFIRMATION: [MessageHandler(Filters.text & ~Filters.command, confirmation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(add_position_conv_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
