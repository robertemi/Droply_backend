import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
import os

load_dotenv()

# Database settings
database_name = os.environ.get('database')
database_user = os.environ.get('user')
database_password = os.environ.get('password')

# Database configuration
DB_CONFIG = {
    "database": database_name,
    "user": database_user,
    "password": database_password,
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
    DATABASE = DB_CONFIG

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')