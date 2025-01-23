import discord
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name='test', aliases=['t'], help='Test if the bot is active', usage='test')
    async def test(self, ctx):
        await ctx.send('Tested, I am active!')

    @commands.command(name='refresh', aliases=['r'], help='Refresh the bot')
    async def refresh(self, ctx):
        extensions = list(self.bot.extensions.keys())
        for ext in extensions:
            await self.bot.reload_extension(ext)  # Reload each extension
        await ctx.send('Refreshed!')

    @commands.command(name='***', aliases=['*'])
    async def bal(self, ctx):
        await ctx.send('Bal')

async def setup(bot):
    await bot.add_cog(General(bot))
