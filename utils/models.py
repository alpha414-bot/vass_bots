import uuid
from sqlalchemy import (
    JSON,
    BigInteger,
    DateTime,
)
from sqlalchemy.orm import mapped_column
from database import Base
from datetime import datetime


# Alternatively, using UUID
def generate_uuid():
    return uuid.uuid4().hex  # This will also give a 32-character hex string


class QuoteData(Base):
    __tablename__ = "quote_data"

    id = mapped_column(BigInteger, primary_key=True, index=True)
    request_data = mapped_column(JSON, nullable=True)
    response_data = mapped_column(JSON, nullable=True)
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    updated_at = mapped_column(DateTime, default=datetime.utcnow)
