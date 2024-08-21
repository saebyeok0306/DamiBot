import asyncio
import signal
import sys
from typing import Any

import discord
from discord.ext import commands
from discord.ext.commands import Context, errors
from discord.ext.commands._types import BotT
from dotenv import dotenv_values
from dotenv import load_dotenv

import utils
import db
from db import SessionContext

load_dotenv(verbose=True, override=True)


class DamiBot(commands.Bot):
    bot_app_info: discord.AppInfo
    test_flag: bool

    def __init__(self, test_flag: bool) -> None:
        super().__init__(command_prefix='@', case_insensitive=True,
                         intents=discord.Intents.all())

        if test_flag is False:
            self.remove_command('help')
        self.test_flag = test_flag
        self.bot_profile_url = "https://github.com/westreed/DamiBot/blob/main/docs/img/profile.png"

    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner

    async def setup_hook(self):
        try:
            self.owner_id = int(config['OWNER_ID'])  # type: ignore
        except KeyError:
            self.bot_app_info = await self.application_info()
            self.owner_id = self.bot_app_info.owner.id

    async def on_ready(self) -> None:
        if self.test_flag:
            guild = self.get_guild(1267660875989520539)
            print(f"테스트 모드로 실행됩니다.\n테스트서버 : {guild}")
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

    async def start(self, token) -> None:
        return await super().start(token, reconnect=True)  # type: ignore

    async def on_command_error(self, context: Context[BotT], exception: errors.CommandError, /) -> None:
        import traceback
        # 오류 메시지를 터미널에 출력
        print(f"An error occurred: {exception}")
        # 로그를 통해서 더 많은 정보를 확인하고 싶으면 logging 모듈을 사용할 수도 있습니다.
        traceback.print_exception(type(exception), exception, exception.__traceback__)

    async def on_error(self, event_method: str, /, *args: Any, **kwargs: Any) -> None:
        import traceback
        # 이벤트 핸들러에서 발생한 오류를 처리
        print(f"An error occurred in {event_method}:")
        traceback.print_exc()


def handle_signal(signal_number, frame):
    # 봇 종료 전에 수행할 작업
    print("봇이 종료됩니다.")
    with SessionContext() as session:
        session.expire_all()
    sys.exit(0)


if __name__ == '__main__':
    # argv --test 포함시 테스트봇으로 실행됨.
    test_flag = utils.is_test_version()
    config = dotenv_values(".env")

    discord_token = config['DISCORD_TOKEN']

    db.init_db(test_flag)
    utils.MusicDat()

    bot = DamiBot(test_flag)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    asyncio.run(bot.load_extension(f'core.Event'))
    asyncio.run(bot.start(token=discord_token))