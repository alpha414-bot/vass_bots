from sqlalchemy import (
    String,
    DateTime,
    BigInteger,
)
from sqlalchemy.orm import mapped_column
from database import Base
from datetime import datetime


class QuoteData(Base):
    __tablename__ = "quote_data"

    uid = mapped_column(BigInteger, primary_key=True, index=True)
    id_richiesta = mapped_column(String(100), nullable=True)
    targa = mapped_column(String(100), nullable=True)
    cf = mapped_column(String(100), nullable=True)
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    updated_at = mapped_column(DateTime, default=datetime.utcnow)
