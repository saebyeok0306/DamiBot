import os

from discord.ext import commands
from discord.ext.commands import Context

from app import DamiBot


class Admin(commands.Cog):
    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot: DamiBot = bot

    @commands.command()
    async def 싱크(self, ctx: Context):
        for guild in self.bot.guilds:
            self.bot.tree.copy_global_to(guild=guild)
            await self.bot.tree.sync(guild=guild)
        msg = await ctx.reply(f'명령어 동기화가 완료되었습니다.')
        await msg.delete(delay=10)
        await ctx.message.delete(delay=10)

    @commands.command()
    async def 언싱크(self, ctx: Context):
        for guild in self.bot.guilds:
            self.bot.tree.clear_commands(guild=guild)
            await self.bot.tree.sync(guild=guild)
        msg = await ctx.reply(f'명령어 동기화를 해제합니다.')
        await msg.delete(delay=10)
        await ctx.message.delete(delay=10)


async def setup(bot):
    await bot.add_cog(Admin(bot))
