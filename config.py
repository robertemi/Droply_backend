import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
import os
from urllib.parse import urlparse

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Parse the URL into components (for psycopg2)
    parsed_url = urlparse(DATABASE_URL)
    DB_CONFIG = {
        "database": parsed_url.path[1:],  # Remove leading '/'
        "user": parsed_url.username,
        "password": parsed_url.password,
        "host": parsed_url.hostname,
        "port": parsed_url.port,
    }
else:
    # Fallback to local .env (for development)
    DB_CONFIG = {
        "database": os.environ.get('database'),
        "user": os.environ.get('user'),
        "password": os.environ.get('password'),
        "host": os.environ.get('host', 'localhost'),
        "port": os.environ.get('port', '5432'),
    }

# Connection pool (optional but recommended)
connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    **DB_CONFIG
)

def get_db_connection():
    """Get a connection from the pool"""
    return connection_pool.getconn()

def return_db_connection(conn):
    """Return connection to the pool"""
    connection_pool.putconn(conn)

# Flask Configuration Class
class Config:
    """Flask application configuration"""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

    # Server settings
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))

    # Database settings - reuse the same settings for Flask if needed
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')