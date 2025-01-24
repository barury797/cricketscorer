import discord
from discord.ext import commands
from discord.ui import Select, View
from livescore import matches_data, match_data

class Scores(commands.Cog):
    def __init__(self, bot): 
        self.matches_data = None
        self.bot = bot

    @commands.command(name='score', aliases=['s'], help='Get live cricket score', usage='score <match_index>')
    async def score(self, ctx, match_index: int):
        if not self.matches_data: self.matches_data = await matches_data() 
        data = await match_data(self.matches_data[match_index-1]['link'], category='all')
        print(data)

        if not data: await ctx.send("Could not fetch match data.")
        
        embed = discord.Embed(
            title = f"`{data['teams']['t1n']:<24} {data['teams']['t1s']:<6}`\n`{data['teams']['t2n']:<24} {data['teams']['t2s']:<6}`",
            color = discord.Color.blue()
        )
        emoji_map = {
            '•': '<:0runs:1332339862719955066>',
            '1': '<:1run:1332339852036935812>',
            '1w': '<:1run:1332339852036935812>',
            '2': '<:2runs:1332339857598447748>',
            '3': '<:3runs:1332339860559761488>',
            '4': '<:4runs:1332339865022496828>',
            '5': '<:5runs:1332339869904670801>',
            '6': '<:6runs:1332339867887337594>',
            'W': '<:wicket:1332341339169361940>'
            # Add more mappings as needed
        }

        # Extract and flatten the timeline data with emoji replacements
        balls = [(over, emoji_map.get(ball, ball)) for over in sorted(data['match']['timeline'].keys(), reverse=True) for ball in data['match']['timeline'][over]]
        last_8_balls = balls[:20]

        formatted_balls, prev_over = [], last_8_balls[0][0]
        for over, ball in last_8_balls:
            if over != prev_over: formatted_balls.append('<:divider:1332346301207023707>')
            formatted_balls.append(ball)
            prev_over = over
        formatted_balls_str = ' '.join([ball for ball in formatted_balls])

        # Add the field to the embed
        embed.add_field(
            name=data['match']['status'], 
            value=f"{formatted_balls_str}", 
            inline=False
        )
        if data['bt1']['name']:
            bt1n = f'{data['bt1']['name']} {data['bt1']['style']}'
            bt2n = f'{data['bt2']['name']} {data['bt2']['style']}'
            bw1n = f'{data['bw1']['name']} {data['bw1']['style']}'
            bw2n = f'{data['bw2']['name']} {data['bw2']['style']}'
            embed.add_field(
                name = f"`{'BATTERS':<24} {'R':<3} {'B':<3} {'SR':<3}`", inline = False,
                value = f"""`{bt1n:<24} {data['bt1']['runs']:<3} {data['bt1']['balls']:<3} {round(float(data['bt1']['sr'])):<3}`\n`{bt2n:<24} {data['bt2']['runs']:<3} {data['bt2']['balls']:<3} {round(float(data['bt2']['sr'])):<3}`""",
            )
            embed.add_field(
                name = f"`{'BOWLERS':<22} {'O':<4} {'M':<2} {'R':<3} W`", inline = False,
                value = f"""`{bw1n:<22} {data['bw1']['overs']:<4} {data['bw1']['maiden']:<2} {data['bw1']['runs']:<3} {data['bw1']['wkts']}`\n`{bw2n:<22} {data['bw2']['overs']:<4} {data['bw2']['maiden']:<2} {data['bw1']['runs']:<3} {data['bw2']['wkts']}`""",
            )
        
        # partnership = f"P'Ship: {data['teams']['t2s']} CRR: {data['match']['crr']} RRR: {data['match']['rrr']}\n"
        
        # timeline = f"**Timeline**\n"
        # timeline += f"{data['match']['timeline']}\n"
        
        # embed.add_field(name="Status", value=data['match']['status'], inline=False)
        # embed.add_field(name="Batters", value=batters, inline=False)
        # embed.add_field(name="Partnership", value=partnership, inline=False)
        # embed.add_field(name="Bowlers", value=bowlers, inline=False)
        # embed.add_field(name="Timeline", value=timeline, inline=False)

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