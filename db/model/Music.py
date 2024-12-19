from __future__ import annotations

from sqlalchemy import String, Column, Integer

from db.Database import Base


class Music(Base):
    __tablename__ = "DJMAX_MUSIC"

    id = Column(Integer, primary_key=True, autoincrement=True)
    music_name = Column(String(200))
    music_artist = Column(String(100))
    music_bpm = Column(String(50))
    music_dlc = Column(String(200))
    music_nickname = Column(String(200))

    def __init__(self, music_name, music_artist, music_bpm, music_dlc, music_nickname=None):
        self.music_name = music_name
        self.music_artist = music_artist
        self.music_bpm = music_bpm
        self.music_dlc = music_dlc
        self.music_nickname = music_nickname

    def __str__(self):
        return f"Music({self.id}, {self.music_name}, {self.music_artist}, {self.music_bpm}, {self.music_dlc})"

    def toDocment(self):
        document = self.__dict__
        document["content"] = f"{self.music_name.lower()} {self.music_artist.lower()} {self.music_nickname}"
        return document

    def __eq__(self, other: Music):
        if self.music_name != other.music_name:
            return False
        if self.music_dlc != other.music_dlc:
            return False
        if self.music_artist != other.music_artist:
            return False
        return True

    def is_update(self, other: Music):
        if not self.__eq__(other):
            return False

        if self.music_nickname != other.music_nickname:
            return True

        return False
