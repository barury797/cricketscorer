import discord
from discord.ext import commands
from tabulate import tabulate
from datetime import date
from cricket_guru.cgstats import get_head_to_head, get_team_record, add_match, get_match

class CGStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def make_table(self, title, header, data):
        return f"**{title}**\n```{tabulate(data, headers=header, tablefmt='rounded_outline')}```"
    
    async def match_embed(self, match_data):
        """Create an embed from match data tuple"""
        id, match_date, total_balls, team1, team1_runs, team1_wickets, team1_balls, team2, team2_runs, team2_wickets, team2_balls, winner = match_data
        
        team1_score = f"{team1_runs}/{team1_wickets}"
        team2_score = f"{team2_runs}/{team2_wickets}"
        team1_overs = f"{team1_balls // 6}.{team1_balls % 6}"
        team2_overs = f"{team2_balls // 6}.{team2_balls % 6}"
        total_overs = round(float(f"{total_balls // 6}.{total_balls % 6}"))
        
        if team1_runs > team2_runs:
            result = f"{winner.upper()} won by {abs(team1_runs - team2_runs)} run"
            result = result + 's' if abs(team1_runs - team2_runs) > 1 else result
        elif team1_runs < team2_runs:
            result = f"{winner.upper()} won by {10 - team2_wickets} wicket"
            result = result + 's' if 10 - team2_wickets > 1 else result
        else:
            result = f"Match tied! but {winner.upper()} won by Super Over"
        
        embed = discord.Embed(title=f"{team1.upper()} vs {team2.upper()}", color=discord.Color.green())
        embed.add_field(name="Date", value=match_date)
        embed.add_field(name="Format", value=f"{total_overs} overs")
        embed.add_field(name="** **", value="** **")
        embed.add_field(name=team1.upper(), value=f"{team1_score} ({team1_overs})")
        embed.add_field(name=team2.upper(), value=f"{team2_score} ({team2_overs})")
        embed.add_field(name="Result", value=result, inline=False)
        embed.set_footer(text=f"Match ID: {id}")
        return embed
    
    @commands.hybrid_command(name='addmatch', help='Add a cricket match result (Admin only)')
    @commands.has_permissions(administrator=True)
    async def add_match_cmd(self, ctx, total_overs: str, team1: str, team1_score: str, team1_overs: str, 
                           team2: str, team2_score: str, team2_overs: str, winner: str = None):
        try:
            # Parse scores and overs
            team1_runs, team1_wickets = map(int, team1_score.split('/'))
            team2_runs, team2_wickets = map(int, team2_score.split('/'))
            
            # Convert overs to balls
            def overs_to_balls(overs):
                parts = overs.split('.')
                return int(parts[0]) * 6 + (int(parts[1]) if len(parts) > 1 else 0)
                
            team1_balls = overs_to_balls(team1_overs)
            team2_balls = overs_to_balls(team2_overs)
            total_balls = overs_to_balls(total_overs)
            
            # Determine winner if not provided
            if not winner:
                if team1_runs == team2_runs:
                    return await ctx.send("Scores are tied! Winner must be specified.")
                winner = team1 if team1_runs > team2_runs else team2
            
            # Add match and get match id
            match_id = await add_match(
                date.today().strftime("%Y-%m-%d"), 
                total_balls,
                team1, team1_runs, team1_wickets, team1_balls,
                team2, team2_runs, team2_wickets, team2_balls,
                winner
            )
            
            if match_id:
                match_data = await get_match(match_id)
                if match_data:
                    embed = await self.match_embed(match_data)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Match added but couldn't retrieve details.")
            else:
                await ctx.send("Failed to add match. Check inputs and try again.")
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")

    @commands.hybrid_command(name='cgm', help='Get match data by ID')
    async def get_match_cmd(self, ctx, match_id: int = commands.parameter(description="Match ID")):
        try:
            match_data = await get_match(match_id)
            if not match_data:
                return await ctx.send(f"No match found with ID: {match_id}")
            
            embed = await self.match_embed(match_data)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error retrieving match: {str(e)}")

    @commands.hybrid_command(name='h2h', help='Get head-to-head record between two teams')
    async def head_to_head(self, ctx, team1: str = commands.parameter(description="First team code"), 
                          team2: str = commands.parameter(description="Second team code")):
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

    @commands.hybrid_command(name='teamstats', help='Get team wins and losses')
    async def team_record(self, ctx, team: str = commands.parameter(description="Team code")):
        result = await get_team_record(team)
        if not result:
            return await ctx.send(f"No data for {team.upper()}.")
            
        table = await self.make_table(
            f"{team.upper()} Wins & Loss", 
            ["Wins", "Loss"], 
            [[result[0], result[1]]]
        )
        await ctx.send(table)
    
    @add_match_cmd.error
    async def add_match_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You need admin permissions to add matches.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Format: `c. addmatch total_overs team1 team1_score team1_overs team2 team2_score team2_overs [winner]`")
        else:
            await ctx.send(f"Error: {str(error)}")

async def setup(bot):
    await bot.add_cog(CGStats(bot))