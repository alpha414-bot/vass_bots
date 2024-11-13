import random
import string
from sqlalchemy import (
    JSON,
    DateTime,
    BigInteger,
)
from sqlalchemy.orm import mapped_column
from database import Base
from datetime import datetime


# Using UUID
def generate_uuid():
    return "".join(random.choices(string.ascii_letters + string.digits, k=32))


class QuoteData(Base):
    __tablename__ = "quote_data"

    id = mapped_column(BigInteger, primary_key=True, index=True, default=generate_uuid)
    request_data = mapped_column(JSON, nullable=True)
    response_data = mapped_column(JSON, nullable=True)
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    updated_at = mapped_column(DateTime, default=datetime.utcnow)
