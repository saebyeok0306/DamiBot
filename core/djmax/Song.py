from io import BytesIO
from typing import Literal

import discord
from discord import app_commands, Interaction, User
from sqlalchemy import and_, desc

import utils
from app import DamiBot
from core.djmax.ReplyRecord import ReplyRecord
from db import SessionContext
from db.model.Music import Music
from db.model.Record import Record
from db.model.SubLevel import SubLevel


class Song(ReplyRecord):
    def __init__(self, bot):
        self.bot: DamiBot = bot

    @app_commands.command(description='내 기록을 조회합니다. 유저를 지정하면 다른 유저의 기록을 볼 수 있어요.')
    @app_commands.describe(title="곡이름", button="버튼수", level="난이도", user="다른 유저의 기록보기")
    @app_commands.autocomplete(title=utils.autocomplete_title)
    async def 기록보기(self, action: Interaction[DamiBot], title: str, button: Literal['4B', '5B', '6B', '8B'],
                   level: Literal['NORMAL', 'HARD', 'MAXIMUM', 'SC'], user: User = None):
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

        # await action.response.defer()
        music = await utils.get_music_from_title(self.bot, action.message, music_title, action=action)

        user_id = action.user.id if user is None else user.id
        user_name = action.user.display_name if user is None else user.display_name

        record_list = []
        with SessionContext() as session:
            record_list = session.query(Record).filter(and_(
                Record.user_id == user_id, Record.music_id == music.id, Record.level == level, Record.button == button)
            ).order_by(desc(Record.id)).limit(5).all()

        if len(record_list) == 0 or record_list is None:
            await action.response.send_message(content=f"{music_title} 곡에 대한 기록이 없습니다.")
            return

        sub_lv = 0
        with SessionContext() as session:
            sub_level = session.query(SubLevel).filter(
                and_(SubLevel.music_id == music.id, SubLevel.music_level == level, SubLevel.music_button == button)
            ).first()
            sub_lv = sub_level.music_sub_level if sub_level is not None else 0

        embed, image_file = self.reply_record(self.bot, music, "⚡ 기록 조회", f"{user_name}님의 기록입니다.", music.music_name, record_list[0], sub_lv)
        await action.response.send_message(embed=embed, file=image_file)

        if len(record_list) > 1:
            plot = utils.ScorePlot(self.bot, music, score_list=record_list)
            img_path = plot.single_user_plot()
            await action.followup.send(file=discord.File(img_path))

    @app_commands.command(description='DJMAX RESPECT V의 수록곡을 검색합니다.')
    @app_commands.describe(query="검색어")
    @app_commands.autocomplete(query=utils.autocomplete_title)
    async def 디맥검색(self, action: Interaction[DamiBot], query: str):
        music_manager = utils.MusicManager()
        return_list = []
        try:
            result = music_manager.search_engine.search(query)
        except Exception as e:
            await action.response.send_message(f"검색 엔진에 오류가 발생했습니다.\n{e}")
            print(e)
            return
        for index, score in result:
            if score < 0.1 or len(return_list) >= 10:
                break
            return_list.append((score, music_manager.all_music_doc[index]))

        if len(return_list) == 0:
            music_title_list = music_manager.get_all_music()
            if query in music_title_list:
                with SessionContext() as session:
                    music_list = session.query(Music).filter(Music.music_name == query).all()
                    for music in music_list:
                        return_list.append((1.0, music.toDocment()))
            else:
                await action.response.send_message("검색 결과가 없습니다.")
                return
        try:
            image_file = discord.File(BytesIO(return_list[0][1]['music_thumbnail']), filename="thumbnail.jpg")

            embed = discord.Embed(title=f"검색결과", description=f"검색어 : `{query}`", color=0x8d76bc)
            embed.set_footer(text=f"DJMAX RESPECT V｜기록 관리봇 담이", icon_url=self.bot.user.display_avatar)
            embed.set_thumbnail(url="attachment://thumbnail.jpg")
            for idx, music in enumerate(return_list):
                score, data = music
                embed.add_field(name=f"{idx + 1}. {data['music_name']}",
                                value=f"`Artist` {data['music_artist']}\n{data['music_dlc']} 수록됨.", inline=False)
        except Exception as e:
            await action.response.send_message(f"검색 결과를 표시하는데 실패했습니다.\n{e}")
            return

        await action.response.send_message(embed=embed, file=image_file)

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