import math

import discord
from discord import Message
from sqlalchemy import and_, desc

import utils
from app import DamiBot
from core.djmax.ReplyRecord import ReplyRecord
from db import SessionContext
from db.model.Record import Record
from db.model.SubLevel import SubLevel
from exception import AnalyzeError, ImageError


class Uploader(ReplyRecord):
    def __init__(self, bot):
        self.bot: DamiBot = bot

        self.system_msg = []
        with open("system.message.json", "r", encoding="UTF-8") as f:
            import json
            system_msgs = json.loads(f.read())
            for system_msg in system_msgs["messages"]:
                msg = {"role": "system", "content": system_msg.rstrip()}
                self.system_msg.append(msg)

    @staticmethod
    def judgement_text(judge_dict: dict):
        if len(judge_dict.keys()) != 12:
            raise AnalyzeError("판정 데이터가 없습니다.")

        # 키 텍스트에 "100%"가 포함된 키를 제외한 나머지 키값들이 0인 경우
        if all([v == 0 for k, v in judge_dict.items() if "100%" not in k]):
            return "PERFECT PLAY"

        for k, v in judge_dict.items():
            if "BREAK" in k and v == 0:
                return "MAX COMBO"

        return "CLEAR"

    @staticmethod
    def judgement_detail(judge_dict: dict):
        return ".".join(list(map(lambda x: str(x), judge_dict.values())))

    @staticmethod
    def judgement_percent(user_score: int):
        percent = math.floor(user_score / 100) / 100
        if percent > 100:
            raise AnalyzeError("점수를 확인할 수 없습니다.")

        return f"{percent:.2f}"

    @staticmethod
    def level(level_text: str):
        # lv가 "NORMAL", "HARD", "MAXIMUM", "SC" 중 하나인 경우
        result = utils.get_music_level_index(level_text)
        if result is False:
            raise AnalyzeError("난이도를 확인할 수 없습니다.")
        return result

    @staticmethod
    def button(button_text: str):
        # button_text에 4, 5, 6, 8 중 하나가 포함된 경우
        for button in ["4", "5", "6", "8"]:
            if button in button_text:
                return button

        raise AnalyzeError("버튼 데이터를 확인할 수 없습니다.")


    def exception_proccess(self, title: str, artist: str):
        check_exception = set([title, artist])
        exception_case = [("L", "Ice")]

        for case in exception_case:
            if case[0] in check_exception and case[1] in check_exception:
                return [True, case[0]]

        return [False, None]


    async def 기록(self, message: Message, result: discord.Attachment):
        try:
            purifier_base64_image = utils.purifier(result.url)
            prompt = self.system_msg + [{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{purifier_base64_image}"}}]
            }]
            result = await utils.call_chatgpt(prompt)

            if result["error"] is not False:
                await message.reply("시간이 초과되었습니다. 다시 시도해주세요.", mention_author=False)
                return

            import json
            from datetime import datetime, timezone, timedelta

            result = result["response"].replace("```json", "").replace("```", "")
            json_result = json.loads(result)
            print(json_result)

            user_id = message.author.id
            temp_title = json_result.get("곡이름") or json_result.get("곡명") or json_result.get("곡 이름")
            title, title_score = utils.most_similar_title(temp_title)
            print(f"search result: {title}:{title_score}")
            
            is_except, ex_title = self.exception_proccess(temp_title, json_result.get('아티스트'))
            if is_except is True:
                title = ex_title
                title_score = 1.0
                print(f"exception case: {title}:{title_score}")

            if title_score <= 0.1:
                print(f"아티스트 이름으로 재검색합니다. 아티스트 :{json_result.get('아티스트')}")
                title, title_score = utils.most_similar_title(json_result.get("아티스트"))
                if title_score <= 0.1:
                    raise AnalyzeError("제목이 잘못 표기되었습니다.")

            music = await utils.get_music_from_title(self.bot, message, title)

            level = self.level(json_result["난이도"])
            button = self.button(json_result.get("버튼") or json_result.get("버튼수") or json_result.get("버튼 수"))

            user_score = int(json_result["점수"])
            judge = self.judgement_percent(user_score)
            judge_detail = self.judgement_detail(json_result["판정상세"])
            judge_text = self.judgement_text(json_result["판정상세"])

            kst = timezone(timedelta(hours=9))
            record_time = int(datetime.now(kst).timestamp())

            with SessionContext() as session:
                last_records = session.query(Record)\
                    .filter(and_(
                        Record.user_id == user_id, Record.music_id == music.id, Record.level == level,
                        Record.button == button)
                    ).order_by(desc(Record.id)).limit(4).all()

                sub_level = session.query(SubLevel).filter(
                    and_(SubLevel.music_id == music.id, SubLevel.music_level == level, SubLevel.music_button == button)
                ).first()
                sub_lv = sub_level.music_sub_level if sub_level is not None else 0

                last_record = None
                if last_records:
                    last_record = last_records[0]
                    description = None
                    if last_record.score > user_score:
                        description = "아쉽게도 신기록이 아니네요.\n가장 높았던 이전 기록을 보여드릴게요."
                    elif last_record.score == user_score:
                        description = "이전에 이미 올리신 기록이에요."

                    if description is not None:
                        embed, image_file = self.reply_record(self.bot, music, "⚡ 이전 기록", description, title, last_record, sub_lv)
                        await message.reply(embed=embed, file=image_file,
                                            mention_author=False)
                        return

                record = Record(user_id=user_id, music_id=music.id, level=level, button=button, judge=judge,
                                judge_detail=judge_detail, judge_text=judge_text, score=user_score,
                                record_time=record_time)
                session.add(record)
                session.commit()

                last_records.insert(0, record)

                embed, image_file = self.reply_record(self.bot, music, "👑 신기록", None, title, record, sub_lv, last_record)
                await message.reply(embed=embed, file=image_file,
                                    mention_author=False)
                if len(last_records) > 1:
                    plot = utils.ScorePlot(self.bot, music, score_list=last_records)
                    img_path = plot.single_user_plot()
                    await message.channel.send(file=discord.File(img_path))

        except AnalyzeError as e:
            print(f"DJMAX RESPECT V의 결과화면을 업로드해야 합니다.\n{e}")
            # await message.reply(f"DJMAX RESPECT V의 결과화면을 업로드해야 합니다.", mention_author=False)
            return
        except ImageError as e:
            print(f"이미지를 분석하는데 실패했습니다.\n{e}")
            # await message.reply(f"이미지를 분석하는데 실패했습니다.\n{e}", mention_author=False)
            return

        except Exception as e:
            print(f"DJMAX 기록 중 오류 발생\n{result.url}\n{e}")
            await utils.send_log(self.bot, f"DJMAX 기록 중 오류 발생\n{result.url}\n{e}")
            # await message.reply(f"이미지를 분석하는데 실패했습니다.\n{e}", mention_author=False)
            return
