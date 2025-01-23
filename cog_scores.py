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
        match_url = self.matches_data[match_index]['link']
        data = await match_data(match_url, category='all')
        if not data:
            await ctx.send("Could not fetch match data.")
            return

        embed = discord.Embed(title=f"{data['teams']['t1n']} vs {data['teams']['t2n']}", color=discord.Color.green())
        embed.add_field(name=data['teams']['t1n'], value=f"{data['teams']['t1s']} ({data['teams']['t1o']})", inline=True)
        embed.add_field(name=data['teams']['t2n'], value=f"{data['teams']['t2s']} ({data['teams']['t2o']})", inline=True)
        embed.add_field(name="Status", value=data['match']['status'], inline=False)
        embed.add_field(name="Current Run Rate", value=data['match']['crr'], inline=True)
        embed.add_field(name="Required Run Rate", value=data['match']['rrr'], inline=True)
        
        embed.add_field(name="Batters", value=f"{data['bt1']['name']} - {data['bt1']['runs']}({data['bt1']['balls']}) SR: {data['bt1']['sr']}\n{data['bt2']['name']} - {data['bt2']['runs']}({data['bt2']['balls']}) SR: {data['bt2']['sr']}", inline=False)
        embed.add_field(name="Bowlers", value=f"{data['bw1']['name']} - {data['bw1']['wkts']}/{data['bw1']['runs']} in {data['bw1']['overs']} overs\n{data['bw2']['name']} - {data['bw2']['wkts']}/{data['bw2']['runs']} in {data['bw2']['overs']} overs", inline=False)

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
            options.append(discord.SelectOption(label=f"{index}. {teams}", description=match_status, value=str(index-1)))
        
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