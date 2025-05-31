import asyncio

from discord import Message
from discord.ext import commands

from app import DamiBot
from core.djmax.Song import Song
from core.djmax.Uploader import Uploader
from utils import is_contain_topic_message


class DJMAX(commands.Cog, Uploader, Song):
    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')

        for parent_class in self.__class__.__bases__:
            if parent_class.__name__ == "Cog": continue
            print(f'{parent_class.__name__}가 로드되었습니다.')

        self.bot: DamiBot = bot

        self.system_msg = []
        with open("system.message.json", "r", encoding="UTF-8") as f:
            import json
            system_msgs = json.loads(f.read())
            for system_msg in system_msgs["messages"]:
                msg = {"role": "system", "content": system_msg.rstrip()}
                self.system_msg.append(msg)

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return False

        try:
            if not is_contain_topic_message(message, "#담이"):
                return False
        except Exception:
            return False

        if message.attachments:
            await asyncio.gather(*(self.기록(message, attachment) for attachment in message.attachments))
            return None
        return None
        # if message.attachments and len(message.attachments) == 1:
        # await self.기록(message, message.attachments[0])


async def setup(bot):
    await bot.add_cog(DJMAX(bot))