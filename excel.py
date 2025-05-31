import db
import utils
import requests
from db import SessionContext
from db.model.Music import Music
from db.model.SubLevel import SubLevel


def db_to_excel():
    db.init_db(True)

    with SessionContext() as session:
        all_music = session.query(Music).order_by(Music.id).all()

        print(all_music)

        # all_music을 토대로 music_id만 추출해서 엑셀 파일로 저장
        import pandas as pd

        music_ids = [music.id for music in all_music]
        music_names = [music.music_name for music in all_music]

        schema = {'music_id': music_ids, 'music_name': music_names}
        for key in [4, 5, 6, 8]:
            for lv in ['nm', 'hd', 'mx', 'sc']:
                schema[f"{key}{lv}"] = [0] * len(music_ids)

        print(schema)
        df = pd.DataFrame(schema)
        df.to_excel('music_ids.xlsx', index=False)

def sub_level_to_db():
    db.init_db(True)

    # updated_music_data.xlsx 파일 열기
    import pandas as pd
    df = pd.read_excel('updated_music_data.xlsx')

    # 한줄씩 읽기 (첫번째는 header)
    for index, row in df.iterrows():
        music_id = row['music_id']
        music_name = row['music_name']
        nm4 = row['4nm']
        nm5 = row['5nm']
        nm6 = row['6nm']
        nm8 = row['8nm']
        hd4 = row['4hd']
        hd5 = row['5hd']
        hd6 = row['6hd']
        hd8 = row['8hd']
        mx4 = row['4mx']
        mx5 = row['5mx']
        mx6 = row['6mx']
        mx8 = row['8mx']
        sc4 = row['4sc']
        sc5 = row['5sc']
        sc6 = row['6sc']
        sc8 = row['8sc']

        datas = [
            {"KEY":4, "LV":10, "SUB":nm4},
            {"KEY":5, "LV":10, "SUB":nm5},
            {"KEY":6, "LV":10, "SUB":nm6},
            {"KEY":8, "LV":10, "SUB":nm8},
            {"KEY":4, "LV":20, "SUB":hd4},
            {"KEY":5, "LV":20, "SUB":hd5},
            {"KEY":6, "LV":20, "SUB":hd6},
            {"KEY":8, "LV":20, "SUB":hd8},
            {"KEY":4, "LV":30, "SUB":mx4},
            {"KEY":5, "LV":30, "SUB":mx5},
            {"KEY":6, "LV":30, "SUB":mx6},
            {"KEY":8, "LV":30, "SUB":mx8},
            {"KEY":4, "LV":40, "SUB":sc4},
            {"KEY":5, "LV":40, "SUB":sc5},
            {"KEY":6, "LV":40, "SUB":sc6},
            {"KEY":8, "LV":40, "SUB":sc8},
        ]

        print(music_id, music_name, nm4, nm5, nm6, nm8, hd4, hd5, hd6, hd8, mx4, mx5, mx6, mx8, sc4, sc5, sc6, sc8)
        with SessionContext() as session:
            for data in datas:
                # SubLevel 테이블에 데이터를 추가.
                sub = SubLevel(music_id=music_id, music_button=data["KEY"], music_level=data["LV"], music_sub_level=data["SUB"])
                print(sub)
                session.add(sub)
            session.commit()

def add_thum():
    db.init_db(True)

    with SessionContext() as session:
        all_music = session.query(Music).order_by(Music.id).all()

        for music in all_music:
            print(music)
            url = f"https://devlog.run/res/dami/djmax/{music.id}.jpg"
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception(f"이미지 다운로드 실패: {url}")

            session.query(Music).filter(Music.id == music.id).update({Music.music_thumbnail: response.content})

        session.commit()

if __name__ == "__main__":
    # db_to_excel()
    # sub_level_to_db()
    add_thum()