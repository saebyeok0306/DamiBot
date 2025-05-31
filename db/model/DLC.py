from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import String, Column, Integer, DateTime, Sequence

from db.Database import Base


class DLC(Base):
    __tablename__ = "DJMAX_DLC"

    id = Column(Integer, Sequence('DLC_SEQ'), primary_key=True)
    dlc_name = Column(String(200))
    created_at = Column(DateTime)

    def __init__(self, dlc_name):
        self.dlc_name = dlc_name
        self.created_at = datetime.now(timezone(timedelta(hours=9)))

    def __str__(self):
        return f"DLC({self.id}, {self.dlc_name}, {self.created_at})"

    def toDocment(self):
        document = self.__dict__
        document["content"] = f"{self.dlc_name.lower()} {self.created_at}"
        return document

    def __eq__(self, other: DLC):
        if self.dlc_name != other.dlc_name:
            return False
        return True
