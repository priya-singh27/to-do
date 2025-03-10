import os
import databases
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, Boolean, Float, MetaData, create_engine, ForeignKey

# Database URL - get from environment or use default SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_accounts.db")

# Database objects
database = databases.Database(DATABASE_URL)
metadata = MetaData()

# Credentials table - stores login information
credentials = Table(
    "credentials",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, unique=True),
    Column("password", String),
    Column("is_available", Boolean, default=True),
    Column("cooldown_minutes", Integer, default=10),  # Default cooldown period in minutes
)

# AI tools table - stores information about supported AI tools
tools = Table(
    "tools",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, unique=True),  # e.g., "claude", "chatgpt", etc.
    Column("auth_type", String, default="password"),  # "password", "email_link", "api_key"
    Column("description", String, nullable=True),
)

# Authentication sessions for email-link based services
auth_sessions = Table(
    "auth_sessions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("tool_id", Integer, ForeignKey("tools.id"), index=True),
    Column("credential_id", Integer, ForeignKey("credentials.id"), index=True),
    Column("session_data", String),  # Encrypted cookie/session data
    Column("created_at", Float),  # When this session was created
    Column("expires_at", Float),  # When this session expires
    Column("is_valid", Boolean, default=True),  # Whether this session is still valid
)

# Usage logs table - tracks when credentials are used with which tool
usage_logs = Table(
    "usage_logs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("credential_id", Integer, ForeignKey("credentials.id"), index=True),
    Column("tool_id", Integer, ForeignKey("tools.id"), index=True),
    Column("timestamp", Float),  # Unix timestamp when used
    Column("session_duration", Integer, nullable=True),  # How long the session lasted (seconds)
)

# Engine for creating tables
engine = create_engine(DATABASE_URL)

# Function to create tables
def create_tables():
    metadata.create_all(engine)