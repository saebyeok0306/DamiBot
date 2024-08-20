from sqlalchemy import String, Column, Integer

from db.Database import Base


class Record(Base):
    __tablename__ = "RECORD"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    music_id = Column(Integer)
    level = Column(Integer)
    button = Column(Integer)
    judge = Column(String(10))  # 99.10%
    judge_detail = Column(String(200))  # 100%부터 Break까지 순차적으로 .으로 구분 ex. 999.6.0.0.0.0.0.0.0.0.0.0
    judge_text = Column(String(50))  # PERFECT, MAX COMBO, CLEAR
    score = Column(Integer)
    record_time = Column(Integer)  # Unix Time

    def __init__(self, user_id, music_id, level, button, judge, judge_detail, judge_text, score, record_time):
        self.user_id = user_id
        self.music_id = music_id
        self.level = level
        self.button = button
        self.judge = judge
        self.judge_detail = judge_detail
        self.judge_text = judge_text
        self.score = score
        self.record_time = record_time

    def __str__(self):
        return f"Record({self.id}, {self.user_id}, {self.music_id}, {self.level}, {self.button}, {self.judge}, {self.judge_detail}, {self.judge_text}, {self.score}, {self.record_time})"
