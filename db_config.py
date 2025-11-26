"""Database configuration and async session management"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql+asyncpg://user:password@localhost:5432/att_school'
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging
    pool_pre_ping=True,
    poolclass=NullPool,  # Disable connection pooling for Flask compatibility
    connect_args={
        "timeout": 10,
        "command_timeout": 60,
    }
)

# Create async session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    expire_on_commit=False
)

async def get_async_session():
    """Get an async database session"""
    async with async_session() as session:
        yield session

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        # Tables will be created by Flask-SQLAlchemy migration
        pass
