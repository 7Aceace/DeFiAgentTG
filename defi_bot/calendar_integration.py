import os
import json
import logging
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv
import sqlite3
from sqlite3 import Error

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

def create_connection(db_file):
    """Create a database connection to the SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        logger.error(f"Database connection error: {e}")
    
    return conn

def get_calendar_service():
    """Get a Google Calendar service object."""
    creds = None
    
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_info(json.loads(open('token.json').read()))
    
    # If there are no valid credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # In production, this would use a more sophisticated auth flow
            # For this demo, we'll use environment variables
            client_id = os.getenv('GOOGLE_CLIENT_ID')
            client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
            refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
            
            if client_id and client_secret and refresh_token:
                creds = Credentials(
                    None,
                    refresh_token=refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=client_id,
                    client_secret=client_secret
                )
            else:
                logger.error("Google Calendar credentials not found in environment variables")
                return None
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('calendar', 'v3', credentials=creds)

def create_yield_claim_event(protocol, asset, estimated_date, user_id=None, position_id=None):
    """Create a Google Calendar event for yield claiming."""
    service = get_calendar_service()
    
    if not service:
        logger.error("Failed to get Google Calendar service")
        return None
    
    # Calculate event time (default to 2pm on the estimated date)
    event_date = datetime.fromisoformat(estimated_date)
    start_time = event_date.replace(hour=14, minute=0, second=0)
    end_time = start_time + timedelta(minutes=30)
    
    # Create event details
    event = {
        'summary': f'Claim {asset} Yield from {protocol}',
        'location': f'{protocol} DeFi Protocol',
        'description': f'Time to claim your yield for {asset} from {protocol}. Check gas prices before proceeding.',
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'UTC',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 60},
            ],
        },
    }
    
    try:
        # Insert the event
        calendar_id = 'primary'  # Use the user's primary calendar
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        event_id = event.get('id')
        logger.info(f"Event created: {event.get('htmlLink')}")
        
        # If position_id is provided, update the database
        if position_id and user_id:
            db_path = os.getenv('DATABASE_PATH', 'defi_bot.db')
            conn = create_connection(db_path)
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE positions SET calendar_event_id = ? WHERE id = ? AND user_id = ?",
                        (event_id, position_id, user_id)
                    )
                    conn.commit()
                except Error as e:
                    logger.error(f"Database error: {e}")
                finally:
                    conn.close()
        
        return event_id
    except Exception as e:
        logger.error(f"Failed to create calendar event: {e}")
        return None

def update_yield_claim_event(event_id, protocol, asset, new_date):
    """Update an existing yield claim event."""
    service = get_calendar_service()
    
    if not service:
        logger.error("Failed to get Google Calendar service")
        return False
    
    try:
        # Get the existing event
        calendar_id = 'primary'
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        
        # Update event details
        event_date = datetime.fromisoformat(new_date)
        start_time = event_date.replace(hour=14, minute=0, second=0)
        end_time = start_time + timedelta(minutes=30)
        
        event['summary'] = f'Claim {asset} Yield from {protocol}'
        event['description'] = f'Time to claim your yield for {asset} from {protocol}. Check gas prices before proceeding.'
        event['start'] = {
            'dateTime': start_time.isoformat(),
            'timeZone': 'UTC',
        }
        event['end'] = {
            'dateTime': end_time.isoformat(),
            'timeZone': 'UTC',
        }
        
        # Update the event
        updated_event = service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
        logger.info(f"Event updated: {updated_event.get('htmlLink')}")
        return True
    except Exception as e:
        logger.error(f"Failed to update calendar event: {e}")
        return False

def delete_yield_claim_event(event_id):
    """Delete a yield claim event."""
    service = get_calendar_service()
    
    if not service:
        logger.error("Failed to get Google Calendar service")
        return False
    
    try:
        # Delete the event
        calendar_id = 'primary'
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        logger.info(f"Event deleted: {event_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete calendar event: {e}")
        return False

def list_upcoming_yield_events(max_results=10):
    """List upcoming yield claim events."""
    service = get_calendar_service()
    
    if not service:
        logger.error("Failed to get Google Calendar service")
        return []
    
    try:
        # Get the upcoming events
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        calendar_id = 'primary'
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime',
            q='Claim Yield'  # Search for yield claim events
        ).execute()
        events = events_result.get('items', [])
        
        return events
    except Exception as e:
        logger.error(f"Failed to list calendar events: {e}")
        return []

def sync_position_with_calendar(user_id, position_id):
    """Sync a DeFi position with Google Calendar."""
    db_path = os.getenv('DATABASE_PATH', 'defi_bot.db')
    conn = create_connection(db_path)
    
    if not conn:
        logger.error("Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT protocol, asset, amount, apy, calendar_event_id
            FROM positions
            WHERE id = ? AND user_id = ?
            """,
            (position_id, user_id)
        )
        position = cursor.fetchone()
        
        if not position:
            logger.error(f"Position not found: {position_id}")
            return False
        
        protocol, asset, amount, apy, calendar_event_id = position
        
        # Estimate next claim date based on protocol and asset
        from blockchain_utils import estimate_next_claim_date
        next_claim_date = estimate_next_claim_date(protocol, asset)
        
        if calendar_event_id:
            # Update existing event
            return update_yield_claim_event(calendar_event_id, protocol, asset, next_claim_date)
        else:
            # Create new event
            event_id = create_yield_claim_event(protocol, asset, next_claim_date, user_id, position_id)
            return bool(event_id)
    except Error as e:
        logger.error(f"Database error: {e}")
        return False
    finally:
        conn.close()

def sync_all_positions_with_calendar(user_id):
    """Sync all DeFi positions for a user with Google Calendar."""
    db_path = os.getenv('DATABASE_PATH', 'defi_bot.db')
    conn = create_connection(db_path)
    
    if not conn:
        logger.error("Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id
            FROM positions
            WHERE user_id = ? AND status = 'active'
            """,
            (user_id,)
        )
        positions = cursor.fetchall()
        
        success_count = 0
        for position in positions:
            position_id = position[0]
            if sync_position_with_calendar(user_id, position_id):
                success_count += 1
        
        logger.info(f"Synced {success_count}/{len(positions)} positions with calendar")
        return success_count > 0
    except Error as e:
        logger.error(f"Database error: {e}")
        return False
    finally:
        conn.close()

def setup_calendar_sync_for_new_position(user_id, protocol, asset, amount, position_type='supply', apy=None):
    """Set up calendar sync for a new DeFi position."""
    db_path = os.getenv('DATABASE_PATH', 'defi_bot.db')
    conn = create_connection(db_path)
    
    if not conn:
        logger.error("Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Insert the position
        cursor.execute(
            """
            INSERT INTO positions (user_id, protocol, asset, amount, position_type, apy)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, protocol, asset, amount, position_type, apy)
        )
        conn.commit()
        position_id = cursor.lastrowid
        
        # Sync with calendar
        return sync_position_with_calendar(user_id, position_id)
    except Error as e:
        logger.error(f"Database error: {e}")
        return False
    finally:
        conn.close()

def get_upcoming_yield_claims_for_user(user_id, days_ahead=7):
    """Get upcoming yield claims for a user."""
    db_path = os.getenv('DATABASE_PATH', 'defi_bot.db')
    conn = create_connection(db_path)
    
    if not conn:
        logger.error("Failed to connect to database")
        return []
    
    try:
        # Get all active positions for the user
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, protocol, asset, amount, apy, calendar_event_id
            FROM positions
            WHERE user_id = ? AND status = 'active'
            """,
            (user_id,)
        )
        positions = cursor.fetchall()
        
        upcoming_claims = []
        
        for position in positions:
            position_id, protocol, asset, amount, apy, calendar_event_id = position
            
            # If there's a calendar event, get its details
            if calendar_event_id:
                service = get_calendar_service()
                if service:
                    try:
                        event = service.events().get(calendarId='primary', eventId=calendar_event_id).execute()
                        start_time = event['start'].get('dateTime')
                        if start_time:
                            event_date = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                            now = datetime.now()
                            days_until = (event_date - now).days
                            
                            if 0 <= days_until <= days_ahead:
                                upcoming_claims.append({
                                    'position_id': position_id,
                                    'protocol': protocol,
                                    'asset': asset,
                                    'amount': amount,
                                    'apy': apy,
                                    'claim_date': event_date.strftime('%Y-%m-%d'),
                                    'days_until': days_until
                                })
                    except Exception as e:
                        logger.error(f"Failed to get calendar event: {e}")
        
        return upcoming_claims
    except Error as e:
        logger.error(f"Database error: {e}")
        return []
    finally:
        conn.close()

# Example usage
if __name__ == '__main__':
    # Create a test event
    event_id = create_yield_claim_event(
        protocol='Compound',
        asset='USDC',
        estimated_date='2025-03-25'
    )
    
    if event_id:
        print(f"Created event with ID: {event_id}")
        
        # Update the event
        update_success = update_yield_claim_event(
            event_id=event_id,
            protocol='Compound',
            asset='USDC',
            new_date='2025-03-26'
        )
        
        if update_success:
            print("Successfully updated event")
        
        # List upcoming events
        events = list_upcoming_yield_events()
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"{start} - {event['summary']}")
        
        # Delete the test event
        delete_success = delete_yield_claim_event(event_id)
        if delete_success:
            print("Successfully deleted event")
