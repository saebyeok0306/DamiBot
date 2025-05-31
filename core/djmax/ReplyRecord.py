from io import BytesIO

import discord

import utils
from app import DamiBot
from db.model.Music import Music
from db.model.Record import Record


class ReplyRecord:

    def simplify_details(self, judge_detail: str):
        judge_list = list(map(lambda x: int(x), judge_detail.split(".")))
        return judge_list[0], sum(judge_list[1:11]), judge_list[11]

    def reply_record(self, bot: DamiBot, music: Music, title: str, description: str, music_title: str, record: Record, sub_level: int, last_record: Record = None):
        from datetime import datetime

        image_file = discord.File(BytesIO(music.music_thumbnail), filename="thumbnail.jpg")

        embed = discord.Embed(title=title, description=description, color=0x8d76bc)
        embed.set_thumbnail(url="attachment://thumbnail.jpg")
        embed.set_footer(text=f"DJMAX RESPECT V｜기록 관리봇 담이", icon_url=bot.user.display_avatar)
        lv = [lv for lv, idx in utils.get_music_level().items() if idx == record.level][0]
        embed.add_field(name="Title", value=f"{music_title} ({record.button}B {lv} ★{sub_level})")
        if last_record is None:
            embed.add_field(name="Judgement", value=f"{record.judge}%\n({record.judge_text})")
        else:
            up_judge = utils.diff_float(float(record.judge), float(last_record.judge))
            embed.add_field(name="Judgement", value=f"{record.judge}% `{up_judge}`\n({record.judge_text})")

        if last_record is None:
            simple_details = self.simplify_details(record.judge_detail)
            embed.add_field(name="Details",
                            value=f"{simple_details[0]} MAX 100%\n{simple_details[1]} MAX 1~90%\n{simple_details[2]} BREAK")
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

        embed.add_field(name="RecordTime",
                        value=f"{record_datetime.year}.{record_datetime.month:02}.{record_datetime.day:02} {record_datetime.hour:02}:{record_datetime.minute:02}")
        return [embed, image_file]