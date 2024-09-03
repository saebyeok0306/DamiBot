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

    def __init__(self, music_name, music_artist, music_bpm, music_dlc):
        self.music_name = music_name
        self.music_artist = music_artist
        self.music_bpm = music_bpm
        self.music_dlc = music_dlc

    def __str__(self):
        return f"Music({self.id}, {self.music_name}, {self.music_artist}, {self.music_bpm}, {self.music_dlc})"

    def toDocment(self):
        document = self.__dict__
        document["content"] = f"{self.music_name.lower()} {self.music_artist.lower()} {self.music_nickname}"
        return document
