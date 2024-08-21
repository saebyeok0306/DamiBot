import asyncio
import math
from typing import List

import discord
from discord import Message
from discord.ext import commands
from discord.ext.commands import Context
from sqlalchemy import and_, desc, asc

import utils
from db import SessionContext
from db.model.Music import Music
from db.model.Record import Record
from exception import AnalyzeError


class DJMAX(commands.Cog):
    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot

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
            raise AnalyzeError("AI가 판정을 잘못 표기했습니다.")

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
            raise AnalyzeError("AI가 점수를 잘못 표기했습니다.")

        return f"{percent:.2f}"

    @staticmethod
    def level(level_text: str):
        # lv가 "NORMAL", "HARD", "MAXIMUM", "SC" 중 하나인 경우
        result = utils.get_music_level_index(level_text)
        if result is False:
            raise AnalyzeError("AI가 난이도를 잘못 표기했습니다.")
        return result

    @staticmethod
    def button(button_text: str):
        # button_text에 4, 5, 6, 8 중 하나가 포함된 경우
        for button in ["4", "5", "6", "8"]:
            if button in button_text:
                return button

        raise AnalyzeError("AI가 버튼을 잘못 표기했습니다.")

    @staticmethod
    def simplify_details(judge_detail: str):
        judge_list = list(map(lambda x: int(x), judge_detail.split(".")))
        return judge_list[0], sum(judge_list[1:11]), judge_list[11]

    def reply_record(self, message: Message, title: str, description: str, music_title: str, record: Record, last_record: Record=None):
        from datetime import datetime
        embed = discord.Embed(title=title, description=description, color=0x8d76bc)
        embed.set_thumbnail(url=f"https://devlog.run/res/dami/djmax/{record.music_id}.jpg")
        embed.set_footer(text=f"DJMAX RESPECT V｜기록 관리봇 담이", icon_url=self.bot.user.display_avatar)
        lv = [lv for lv, idx in utils.get_music_level().items() if idx == record.level][0]
        embed.add_field(name="Title", value=f"{music_title} ({record.button}B {lv})")
        if last_record is None:
            embed.add_field(name="Judgement", value=f"{record.judge}%\n({record.judge_text})")
        else:
            up_judge = utils.diff_float(float(record.judge), float(last_record.judge))
            embed.add_field(name="Judgement", value=f"{record.judge}% `{up_judge}`\n({record.judge_text})")

        if last_record is None:
            simple_details = self.simplify_details(record.judge_detail)
            embed.add_field(name="Details", value=f"{simple_details[0]} MAX 100%\n{simple_details[1]} MAX 1~90%\n{simple_details[2]} BREAK")
        else:
            simple_details = self.simplify_details(record.judge_detail)
            last_simple_details = self.simplify_details(last_record.judge_detail)

            max100 = utils.diff_int(simple_details[0], last_simple_details[0])
            max190 = utils.diff_int(simple_details[1], last_simple_details[1])
            mbreak = utils.diff_int(simple_details[2], last_simple_details[2])

            embed.add_field(name="Details",
                            value=f"{simple_details[0]} `({max100})` MAX 100%\n"
                                  f"{simple_details[1]} `({max190})` MAX 1~90%\n"
                                  f"{simple_details[2]} `({mbreak})` BREAK")

        if last_record is None:
            embed.add_field(name="Score", value=f"{record.score}점")
        else:
            up_score = utils.diff_int(record.score, last_record.score)
            embed.add_field(name="Score", value=f"{record.score}점 `({up_score})`")
        # unix timestamp를 datetime으로 변환
        record_datetime = datetime.fromtimestamp(record.record_time)

        embed.add_field(name="RecordTime", value=f"{record_datetime.year}.{record_datetime.month:02}.{record_datetime.day:02} {record_datetime.hour:02}:{record_datetime.minute:02}")
        return embed



    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return False

        try:
            if "#담이" not in message.channel.topic:
                return False
        except AttributeError:
            return False

        if message.attachments:
            await asyncio.gather(*(self.기록(message, attachment) for attachment in message.attachments))
        # if message.attachments and len(message.attachments) == 1:
            # await self.기록(message, message.attachments[0])

    async def 기록(self, message: Message, result: discord.Attachment):
        prompt = self.system_msg + [{
            "role": "user",
            "content": [{"type": "image_url", "image_url": {"url": result.url}}]
        }]
        result = await utils.call_chatgpt(prompt)

        if result["error"] is not False:
            await message.reply("시간이 초과되었습니다. 다시 시도해주세요.", mention_author=False)
            return

        import json
        from datetime import datetime, timezone, timedelta
        try:
            result = result["response"].replace("```json", "").replace("```", "")
            json_result = json.loads(result)

            print(json_result)

            user_id = message.author.id
            title, title_score = utils.most_similar_title(json_result.get("곡이름") or json_result.get("곡명") or json_result.get("곡 이름"))
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
                last_record = session.query(Record).filter(
                    and_(Record.user_id == user_id, Record.music_id == music.id, Record.level == level, Record.button == button)).order_by(desc(Record.id)).first()

                if last_record:
                    description = None
                    if last_record.score > user_score:
                        description = "아쉽게도 신기록이 아니네요.\n가장 높았던 이전 기록을 보여드릴게요."
                    elif last_record.score == user_score:
                        description = "이전에 이미 올리신 기록이에요."

                    if description is not None:
                        await message.reply(embed=self.reply_record(message, "⚡ 이전 기록", description, title, last_record), mention_author=False)
                        return

                record = Record(user_id=user_id, music_id=music.id, level=level, button=button, judge=judge,
                                judge_detail=judge_detail, judge_text=judge_text, score=user_score, record_time=record_time)
                session.add(record)
                session.commit()

                await message.reply(embed=self.reply_record(message, "👑 신기록", None, title, record, last_record), mention_author=False)

        except Exception as e:
            await message.reply(f"이미지를 분석하는데 실패했습니다.\n{e}", mention_author=False)
            return

    @commands.command(name="기록보기")
    async def 기록보기(self, ctx: Context, *messages):
        *music_name, button, level = messages
        music_name = " ".join(music_name)
        button = utils.unify_music_button(button)
        level = utils.get_music_level()[utils.unify_music_level(level)]
        music_title, title_score = utils.most_similar_title(music_name)
        print(music_title)
        if title_score <= 0.1:
            await ctx.reply(f"해당 곡은 데이터베이스에 없습니다.", mention_author=False)
            return

        music = await utils.get_music_from_title(self.bot, ctx.message, music_title)

        record_list = []
        with SessionContext() as session:
            record_list = session.query(Record).filter(and_(
                Record.user_id == ctx.author.id, Record.music_id == music.id, Record.level == level, Record.button == button)
            ).order_by(asc(Record.id)).limit(5).all()

        if len(record_list) == 0:
            await ctx.reply(f"해당 곡에 대한 기록이 없습니다.", mention_author=False)
            return

        await ctx.reply(
            embed=self.reply_record(ctx.message, "⚡ 이전 기록", None, music.music_name, record_list[0]),
            mention_author=False
        )
        plot = utils.ScorePlot(music, score_list=record_list)
        if len(record_list) > 1:
            img_path = plot.single_user_plot()
            await ctx.send(file=discord.File(img_path))





async def setup(bot):
    await bot.add_cog(DJMAX(bot))