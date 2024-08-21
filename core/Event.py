import os

from discord.ext import commands


class Event(commands.Cog):
    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.core_list = ["DJMAX"]

    @commands.Cog.listener()
    async def on_ready(self):
        print('로그인되었습니다!')
        print(self.bot.user.name)
        print(self.bot.user.id)
        print('==============================')

        await self.load_core()

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