import discord
from discord.ext import commands
from discord.ui import Select, View
from livescore import matches_data, match_data

class Scores(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot
        self.matches_data = []

    @commands.command(name='score', aliases=['s'], help='Get live cricket score', usage='score <match_index>')
    async def score(self, ctx, match_index: int):
        match_url = self.matches_data[match_index-1]['link']
        data = await match_data(match_url, category='summary')
        if not data:
            await ctx.send("Could not fetch match data.")
            return
        
        print(data)

        embed = discord.Embed(title=f"{data['t1n']} vs {data['t2n']}", color=discord.Color.green())
        embed.add_field(name=data['t1n'], value=data['t1s'], inline=True)
        embed.add_field(name=data['t2n'], value=data['t2s'], inline=True)
        embed.add_field(name="Status", value=data['status'], inline=False)
        embed.add_field(name="Current Run Rate", value=data['crr'], inline=True)
        embed.add_field(name="Required Run Rate", value=data['rrr'], inline=True)

        await ctx.send(embed=embed)

    @commands.command(name='matches', aliases=['m'], help='Get live cricket matches')
    async def matches(self, ctx):
        self.matches_data = await matches_data()
        if not self.matches_data:
            await ctx.send("No live matches at the moment.")
            return

        embed = discord.Embed(title="Live Cricket Matches", color=discord.Color.blue())
        options = []
        for index, match in enumerate(self.matches_data, start=1):
            teams = " vs ".join(match['score'].keys())
            scores = " | ".join([f"{team}: {score}" for team, score in match['score'].items() if score])
            match_time = match['time'] if match['time'] else ""
            match_status = f'{match['status']}' if match['status'] else ""
            embed.add_field(
                name=f"{index}. {teams} - {match_time}", 
                value=f"⠀ {scores}\n⠀ __{match_status}__" if scores else f"⠀ {match_status}", 
                inline=False
            )
            options.append(discord.SelectOption(label=f"{index}. {teams}", description=match_status, value=str(index)))
        
        select = Select(placeholder="Choose a match to get the score", options=options)

        async def select_callback(interaction):
            match_index = int(select.values[0])  # Extract the index
            await interaction.response.defer()
            await ctx.invoke(self.score, match_index=match_index)

        select.callback = select_callback
        view = View()
        view.add_item(select)

        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Scores(bot))