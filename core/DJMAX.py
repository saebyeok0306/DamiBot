import asyncio
import math
from typing import Literal

import discord
from discord import Message, app_commands, Interaction, User
from discord.ext import commands
from sqlalchemy import and_, desc

import utils
from app import DamiBot
from db import SessionContext
from db.model.Record import Record
from exception import AnalyzeError, ImageError


class DJMAX(commands.Cog):
    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
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

    @staticmethod
    def simplify_details(judge_detail: str):
        judge_list = list(map(lambda x: int(x), judge_detail.split(".")))
        return judge_list[0], sum(judge_list[1:11]), judge_list[11]

    def reply_record(self, title: str, description: str, music_title: str, record: Record, last_record: Record=None):
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
        try:
            purifier_base64_image = utils.purifier(result.url)
            prompt = self.system_msg + [{
                "role": "user",
                "content": [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{purifier_base64_image}"}}]
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
            title, title_score = utils.most_similar_title(json_result.get("곡이름") or json_result.get("곡명") or json_result.get("곡 이름"))
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
                last_records = session.query(Record).filter(and_(
                    Record.user_id == user_id, Record.music_id == music.id, Record.level == level,
                    Record.button == button)
                ).order_by(desc(Record.id)).limit(4).all()

                last_record = None
                if last_records:
                    last_record = last_records[0]
                    description = None
                    if last_record.score > user_score:
                        description = "아쉽게도 신기록이 아니네요.\n가장 높았던 이전 기록을 보여드릴게요."
                    elif last_record.score == user_score:
                        description = "이전에 이미 올리신 기록이에요."

                    if description is not None:
                        await message.reply(embed=self.reply_record("⚡ 이전 기록", description, title, last_record), mention_author=False)
                        return

                record = Record(user_id=user_id, music_id=music.id, level=level, button=button, judge=judge,
                                judge_detail=judge_detail, judge_text=judge_text, score=user_score, record_time=record_time)
                session.add(record)
                session.commit()

                last_records.insert(0, record)

                await message.reply(embed=self.reply_record("👑 신기록", None, title, record, last_record), mention_author=False)
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

    @app_commands.command(description='내 기록을 조회합니다. 유저를 지정하면 다른 유저의 기록을 볼 수 있어요.')
    @app_commands.describe(title="곡이름", button="버튼수", level="난이도", user="다른 유저의 기록보기")
    async def 기록보기(self, action: Interaction[DamiBot], title: str, button: Literal['4B', '5B', '6B', '8B'], level: Literal['NORMAL', 'HARD', 'MAXIMUM', 'SC'], user: User = None):
        button = utils.unify_music_button(button)
        level = utils.get_music_level()[level]
        music_title, title_score = utils.most_similar_title(title)
        print(music_title)
        if title_score <= 0.1:
            music_manager = utils.MusicManager()
            result = music_manager.search_engine.search(title)
            if len(result) == 0 or result[0][1] < 0.1:
                await action.response.send_message("해당 곡은 데이터베이스에 없습니다.", ephemeral=True)
                return
            index, _ = result[0]
            music = music_manager.all_music_doc[index]
            music_title = music["music_name"]

        await action.response.defer()
        message = await action.followup.send("조회 중입니다...")
        music = await utils.get_music_from_title(self.bot, action.message, music_title, action=action)

        user_id = action.user.id if user is None else user.id
        user_name = action.user.display_name if user is None else user.display_name

        record_list = []
        with SessionContext() as session:
            record_list = session.query(Record).filter(and_(
                Record.user_id == user_id, Record.music_id == music.id, Record.level == level, Record.button == button)
            ).order_by(desc(Record.id)).limit(5).all()

        if len(record_list) == 0:
            await message.edit(content=f"{music_title} 곡에 대한 기록이 없습니다.")
            return

        await message.edit(
            content=None,
            embed=self.reply_record("⚡ 기록 조회", f"{user_name}님의 기록입니다.", music.music_name, record_list[0]),
        )

        if len(record_list) > 1:
            plot = utils.ScorePlot(self.bot, music, score_list=record_list)
            img_path = plot.single_user_plot()
            await action.followup.send(file=discord.File(img_path))

    @app_commands.command(description='DJMAX RESPECT V의 수록곡을 검색합니다.')
    @app_commands.describe(query="검색어")
    async def 디맥검색(self, action: Interaction[DamiBot], query: str):
        music_manager = utils.MusicManager()
        try:
            result = music_manager.search_engine.search(query)
        except Exception as e:
            await action.response.send_message(f"검색 엔진에 오류가 발생했습니다.\n{e}")
            print(e)
            return
        return_list = []
        for index, score in result:
            if score < 0.1 or len(return_list) >= 10:
                break
            return_list.append((score, music_manager.all_music_doc[index]))

        if len(return_list) == 0:
            await action.response.send_message("검색 결과가 없습니다.")
            return
        try:
            embed = discord.Embed(title=f"검색결과", description=f"검색어 : `{query}`", color=0x8d76bc)
            embed.set_footer(text=f"DJMAX RESPECT V｜기록 관리봇 담이", icon_url=self.bot.user.display_avatar)
            embed.set_thumbnail(url=f"https://devlog.run/res/dami/djmax/{return_list[0][1]['id']}.jpg")
            for idx, music in enumerate(return_list):
                score, data = music
                embed.add_field(name=f"{idx+1}. {data['music_name']}", value=f"`Artist` {data['music_artist']}\n{data['music_dlc']} 수록됨.", inline=False)
        except Exception as e:
            await action.response.send_message(f"검색 결과를 표시하는데 실패했습니다.\n{e}")
            return

        await action.response.send_message(embed=embed)

    # @commands.command(name="기록보기")
    # async def 기록보기(self, ctx: Context, *messages):
    #     *music_name, button, level = messages
    #     music_name = " ".join(music_name)
    #     button = utils.unify_music_button(button)
    #     level = utils.get_music_level()[utils.unify_music_level(level)]
    #     music_title, title_score = utils.most_similar_title(music_name)
    #     print(music_title)
    #     if title_score <= 0.1:
    #         await ctx.reply(f"해당 곡은 데이터베이스에 없습니다.", mention_author=False)
    #         return
    #
    #     music = await utils.get_music_from_title(self.bot, ctx.message, music_title)
    #
    #     record_list = []
    #     with SessionContext() as session:
    #         record_list = session.query(Record).filter(and_(
    #             Record.user_id == ctx.author.id, Record.music_id == music.id, Record.level == level, Record.button == button)
    #         ).order_by(asc(Record.id)).limit(5).all()
    #
    #     if len(record_list) == 0:
    #         await ctx.reply(f"해당 곡에 대한 기록이 없습니다.", mention_author=False)
    #         return
    #
    #     await ctx.reply(
    #         embed=self.reply_record("⚡ 이전 기록", None, music.music_name, record_list[0]),
    #         mention_author=False
    #     )
    #     plot = utils.ScorePlot(self.bot, music, score_list=record_list)
    #     if len(record_list) > 1:
    #         img_path = plot.single_user_plot()
    #         await ctx.send(file=discord.File(img_path))


async def setup(bot):
    await bot.add_cog(DJMAX(bot))