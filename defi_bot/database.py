# Database schema for DeFi Bot

import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """Create a database connection to the SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    
    return conn

def create_tables(conn):
    """Create the necessary tables for the DeFi bot"""
    
    # Users table
    sql_create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        telegram_id INTEGER NOT NULL UNIQUE,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Wallets table
    sql_create_wallets_table = """
    CREATE TABLE IF NOT EXISTS wallets (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        address TEXT NOT NULL,
        chain TEXT DEFAULT 'ethereum',
        label TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE(user_id, address)
    );
    """
    
    # Positions table
    sql_create_positions_table = """
    CREATE TABLE IF NOT EXISTS positions (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        wallet_id INTEGER,
        protocol TEXT NOT NULL,
        asset TEXT NOT NULL,
        amount REAL NOT NULL,
        position_type TEXT NOT NULL,
        apy REAL,
        start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_date TIMESTAMP,
        status TEXT DEFAULT 'active',
        calendar_event_id TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (wallet_id) REFERENCES wallets (id)
    );
    """
    
    # Alerts table
    sql_create_alerts_table = """
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        alert_type TEXT NOT NULL,
        parameters TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """
    
    # Security checks table
    sql_create_security_checks_table = """
    CREATE TABLE IF NOT EXISTS security_checks (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        contract_address TEXT NOT NULL,
        risk_score INTEGER,
        details TEXT,
        checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """
    
    # Execute table creation
    try:
        c = conn.cursor()
        c.execute(sql_create_users_table)
        c.execute(sql_create_wallets_table)
        c.execute(sql_create_positions_table)
        c.execute(sql_create_alerts_table)
        c.execute(sql_create_security_checks_table)
    except Error as e:
        print(e)

def initialize_database(db_file):
    """Initialize the database with tables"""
    conn = create_connection(db_file)
    
    if conn is not None:
        create_tables(conn)
        conn.close()
        print(f"Database initialized at {db_file}")
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    initialize_database("defi_bot.db")
