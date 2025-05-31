from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import String, Column, Integer, DateTime, ForeignKey, Sequence

from db.Database import Base


class SubLevel(Base):
    __tablename__ = "DJMAX_SUB_LEVEL"

    id = Column(Integer, Sequence('SUB_LEVEL_SEQ'), primary_key=True)
    music_id = Column(Integer, ForeignKey("DJMAX_MUSIC.id"))
    music_button = Column(Integer)
    music_level = Column(Integer)
    music_sub_level = Column(Integer)
    created_at = Column(DateTime)

    def __init__(self, music_id, music_button, music_level, music_sub_level):
        self.music_id = music_id
        self.music_button = music_button
        self.music_level = music_level
        self.music_sub_level = music_sub_level
        self.created_at = datetime.now(timezone(timedelta(hours=9)))

    def __str__(self):
        return f"SubLevel({self.id}, {self.music_id}, {self.music_button}, {self.music_level}, {self.music_sub_level}, {self.created_at})"

    def __eq__(self, other: SubLevel):
        if self.music_id != other.music_id or self.music_level != other.music_level:
            return False
        return True
