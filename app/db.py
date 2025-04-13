import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlmodel import SQLModel, Field, Column, DateTime
from datetime import datetime
from app.config import settings
import uuid
from typing import Optional

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=True if settings.ENVIRONMENT == "development" else False,
    future=True,
)

# Create async session
async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Base model
Base = declarative_base()

# Define SQLModel models
class StakeAction(SQLModel, table=True):
    __tablename__ = "stake_actions"
    
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    action_type: str  # stake or unstake
    netuid: int
    hotkey: str
    amount: float
    sentiment_score: float
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))
    transaction_hash: Optional[str] = None
    status: str = "pending"  # pending, success, failed

class TaoDividendQuery(SQLModel, table=True):
    __tablename__ = "tao_dividend_queries"
    
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    netuid: int
    hotkey: str
    dividend: float
    from_cache: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))

# Create tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    logging.info("Database tables created")

# Dependency to get DB session
async def get_db_session():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


