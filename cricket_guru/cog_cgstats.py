import discord
from discord.ext import commands
from tabulate import tabulate
from cricket_guru.cgstats import get_head_to_head

class CGStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def make_table(self, title, header, data):
        table = tabulate(data, headers=header, tablefmt="rounded_outline", colalign=(None))
        return f"**{title}**\n```{table}```"

# -------------------------------------------------- Commands -------------------------------------------------- #
    @commands.command(name='h2h', help='Get head-to-head record between two teams')
    async def head_to_head(self, ctx, team1: str, team2: str):
        result = await get_head_to_head(team1, team2)
        if not result:
            return await ctx.send(f"No data for {team1.upper()} vs {team2.upper()}.")

        table = await self.make_table(
            f"H2H: {team1.upper()} vs {team2.upper()}",
            ["Stat", team1.upper(), team2.upper()],

            [["Match Wins", result[0], result[1]],
            ["Highest Score", result[2], result[3]],
            ["Lowest Score", result[4], result[5]],
            ["Avg Runs", result[6], result[7]]]
        )
        
        await ctx.send(table)

async def setup(bot):
    await bot.add_cog(CGStats(bot))