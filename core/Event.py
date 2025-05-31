import os

from discord.ext import commands

from app import DamiBot


class Event(commands.Cog):
    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot: DamiBot = bot
        self.core_list = ["Admin", "DJMAX"]

    @commands.Cog.listener()
    async def on_ready(self):
        print('로그인되었습니다!')
        print(self.bot.user.name)
        print(self.bot.user.id)
        print('==============================')
        await self.load_core()

        if self.bot.test_flag:
            guild = self.bot.get_guild(966942556078354502)
            print(f"테스트 모드로 실행됩니다.\n테스트서버 : {guild}")
            self.bot.tree.copy_global_to(guild=guild)
            await self.bot.tree.sync(guild=guild)
        else:
            await self.bot.tree.sync()


    async def load_core(self):
        print("코어모듈을 로드합니다...")
        for filename in os.listdir('core'):
            if filename.endswith('.py'):
                extension_name = filename[:-3]
                if extension_name in self.core_list:
                    try:
                        await self.bot.load_extension(f'core.{extension_name}')
                    except Exception as e:
                        print(f'{extension_name} 로드 실패: {e}')


async def setup(bot):
    await bot.add_cog(Event(bot))