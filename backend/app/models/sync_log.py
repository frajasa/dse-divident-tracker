from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone

from app.database import Base


class SyncLog(Base):
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    sync_type = Column(String(30), nullable=False)  # dividends, prices, status_update
    status = Column(String(20), nullable=False, default="started")  # started, completed, failed
    records_found = Column(Integer, default=0)
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_skipped = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    triggered_by = Column(String(50), default="scheduler")  # scheduler, manual, api
