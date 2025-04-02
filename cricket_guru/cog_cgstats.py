import discord
from discord.ext import commands
from tabulate import tabulate
from datetime import date
from cricket_guru.cgstats import get_head_to_head, get_team_record, add_match

class CGStats(commands.Cog):
    def __init__(self, bot): self.bot = bot

    async def make_table(self, title, header, data):
        return f"**{title}**\n```{tabulate(data, headers=header, tablefmt='rounded_outline', colalign=(None))}```"

    @commands.hybrid_command(name='h2h', help='Get head-to-head record between two teams')
    async def head_to_head(self, ctx, team1: str = commands.parameter(description="First team code"), 
                          team2: str = commands.parameter(description="Second team code")):
        result = await get_head_to_head(team1, team2)
        if not result: return await ctx.send(f"No data for {team1.upper()} vs {team2.upper()}.")
        table = await self.make_table(
            f"H2H: {team1.upper()} vs {team2.upper()}",
            ["Stat", team1.upper(), team2.upper()],
            [["Match Wins", result[0], result[1]], ["Highest Score", result[2], result[3]],
             ["Lowest Score", result[4], result[5]], ["Avg Runs", result[6], result[7]]]
        )
        await ctx.send(table)

    @commands.hybrid_command(name='teamstats', help='Get team wins and losses')
    async def team_record(self, ctx, team: str = commands.parameter(description="Team code")):
        result = await get_team_record(team)
        if not result: return await ctx.send(f"No data for {team.upper()}.")
        table = await self.make_table(
            f"{team.upper()} Wins & Loss", ["Wins", "Loss"], [[result[0], result[1]]]
        )
        await ctx.send(table)
    
    @commands.hybrid_command(name='addmatch', help='Add a cricket match result (Admin only)')
    @commands.has_permissions(administrator=True)
    async def add_match_cmd(self, ctx, total_overs: str, team1: str, team1_score: str, team1_overs: str, 
                           team2: str, team2_score: str, team2_overs: str, winner: str = None):
        try:
            team1_runs = int(team1_score.split('/')[0])
            team2_runs = int(team2_score.split('/')[0])
            
            if team1_runs == team2_runs and not winner:
                return await ctx.send("Scores are tied! Winner must be specified.")
                
            if not winner:
                winner = team1 if team1_runs > team2_runs else team2
                
            result = await add_match(date.today().strftime("%Y-%m-%d"), total_overs, 
                                    team1, team1_score, team1_overs, 
                                    team2, team2_score, team2_overs, winner)
            
            if result:
                embed = discord.Embed(title="Match Added", color=discord.Color.green())
                embed.add_field(name="Date", value=date.today().strftime("%Y-%m-%d"), inline=True)
                embed.add_field(name="Format", value=f"{total_overs} overs", inline=True)
                embed.add_field(name="Winner", value=winner.upper(), inline=True)
                embed.add_field(name=team1.upper(), value=f"{team1_score} ({team1_overs})", inline=True)
                embed.add_field(name=team2.upper(), value=f"{team2_score} ({team2_overs})", inline=True)
                await ctx.send(embed=embed)
            else:
                await ctx.send("Failed to add match. Check inputs and try again.")
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")
    
    @add_match_cmd.error
    async def add_match_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You need admin permissions to add matches.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Format: `!addmatch total_overs team1 team1_score team1_overs team2 team2_score team2_overs [winner]`")
        else:
            await ctx.send(f"Error: {str(error)}")

async def setup(bot):
    await bot.add_cog(CGStats(bot))