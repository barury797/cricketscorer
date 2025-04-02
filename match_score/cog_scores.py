# cog_scores.py

import asyncio
import time
import discord
from discord.ext import commands
from discord.ui import Select, View
from match_score.scores import get_matches, get_match

class Scores(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.MATCHES_CACHE_TTL = 90
        self.MATCH_CACHE_TTL = 30
        self.matches_data = []
        self.matches_last_cache = None
        self.match_data = {}
        self.match_last_cache = {}
        # Emoji map dictionary for ball-by-ball commentary
        self.emoji_map = {
            '•': '<:0r:1332984983681499187>', '1': '<:1r:1332984994326642708>', 
            '2': '<:2r:1332985073972154430>', '3': '<:3r:1332985168771678322>', 
            '4': '<:4r:1332985235226492999>', '5': '<:5r:1332985370094342219>', 
            '6': '<:6r:1332985482698559534>', '1b': '<:1b:1332984986239893534>', 
            '2b': '<:2b:1332985066061697104>', '3b': '<:3b:1332985160198520954>', 
            '4b': '<:4b:1332985227714236487>', '1w': '<:1w:1332984996813865031>', 
            '2w': '<:2w:1332985077021544468>', '3w': '<:3w:1332985171527471104>', 
            '4w': '<:4w:1332985237600337980>', '5w': '<:5w:1332985372623372368>', 
            '1lb': '<:1lb:1332984989100281856>', '2lb': '<:2lb:1332985069060755490>', 
            '3lb': '<:3lb:1332985163466145853>', '4lb': '<:4lb:1332985230100926497>', 
            '1nb': '<:1nb:1332984991545557043>', '2nb': '<:2nb:1332985071237468170>', 
            '3nb': '<:3nb:1332985166246838353>', '4nb': '<:4nb:1332985232525230123>', 
            '5nb': '<:5nb:1332985365048332363>', '6nb': '<:6nb:1332985480043696148>', 
            '7nb': '<:7nb:1332985485198626898>', '5pen': '<:5pen:1332985368005447750>', 
            'W': '<:wk:1332996980066222090>', 'W+1': '<:w1:1332996969651638394>', 
            'W+2': '<:w2:1332996974902906971>', 'W+3': '<:w3:1332996976748531846>'
        }

    @commands.command(name='score', aliases=['s'], help='Get live cricket score', usage='score <match_index>')
    async def score(self, ctx, match_index: int=None):
        if not match_index:
            return await ctx.send(embed=discord.Embed(title="Match index not given.", color=discord.Color.red()))
        await ctx.send(embed=await self.get_score(match_index))

    @commands.command(name='matches', aliases=['m'], help='Get live cricket matches')
    async def matches(self, ctx):
        self.matches_data = await self.get_matches_data()
        if not self.matches_data:
            return await ctx.send("No live matches at the moment.")

        embed = discord.Embed(title="Live Cricket Matches", color=discord.Color.blue())
        options = []
        
        # Build embed and dropdown options
        for i, match in enumerate(self.matches_data, start=1):
            teams = " vs ".join(match['score'].keys())
            scores = " | ".join([f"{team}: {score}" for team, score in match['score'].items() if score])
            
            embed.add_field(
                name=f"{i}. {teams} - {match['time'] or ''}",
                value=f"⠀ {scores}\n⠀ __{match['status']}__" if scores else f"⠀ {match['status']}",
                inline=False
            )
            
            options.append(discord.SelectOption(
                label=f"{i}. {teams}"[:100],  # Discord has a 100-char limit
                description=match['status'][:100] if match['status'] else "",
                value=str(i)
            ))

        # Create dropdown
        select = Select(placeholder="Choose a match to get the score", options=options)
        
        async def select_callback(interaction):
            await interaction.response.defer()
            await ctx.invoke(self.score, match_index=int(select.values[0]))
            
        select.callback = select_callback
        view = View()
        view.add_item(select)
        
        await ctx.send(embed=embed, view=view)

    async def get_matches_data(self):
        """Get matches data with caching"""
        current_time = time.time()
        if not self.matches_last_cache or current_time - self.matches_last_cache > self.MATCHES_CACHE_TTL:
            self.matches_data = await asyncio.to_thread(get_matches)
            self.matches_last_cache = current_time
        return self.matches_data

    async def get_score(self, match_index):
        """Get score for specific match with caching"""
        if not self.matches_data:
            self.matches_data = await self.get_matches_data()
            
        try:
            url = self.matches_data[match_index-1]['link']
        except IndexError:
            return discord.Embed(title="Invalid match index.", color=discord.Color.red())
        
        current_time = time.time()
        if url in self.match_last_cache and current_time - self.match_last_cache[url] < self.MATCH_CACHE_TTL:
            return self.match_data[url]
        
        data = await asyncio.to_thread(get_match, url)
        if not data:
            return discord.Embed(title="Match not found.", color=discord.Color.red())

        # Create teams header
        t1 = f'__{data["teams"]["t1n"]}__: {data["teams"]["t1s"]}'
        t2 = f'__{data["teams"]["t2n"]}__: {data["teams"]["t2s"]}'
        embed = discord.Embed(title=f"{t1}\n{t2}", color=discord.Color.blue())

        # Format recent balls timeline
        balls = [(over, self.emoji_map.get(ball, ball))
            for over in sorted(data['match']['timeline'], reverse=True)
            for ball in data['match']['timeline'][over]][:21]

        formatted_balls = []
        prev_over = None
        for over, ball in balls:
            if over != prev_over and prev_over is not None:
                formatted_balls.append('<:divider:1332996954824900672>')
            formatted_balls.append(ball)
            prev_over = over

        # Add match status
        status2 = "`\n`".join(part.strip() for part in data['match']['status2'].split('•'))
        embed.add_field(
            name=data['match']['status'],
            value=f"{' '.join(formatted_balls)}\n`{status2.strip()}`", 
            inline=False
        )

        # Add batters info
        batter_data = []
        for i in range(1, 3):
            if data.get(f'bt{i}') and data[f'bt{i}'].get('name'):
                batter_data.append(
                    f"`{data[f'bt{i}']['name']:<24} {data[f'bt{i}']['runs']:<3} {data[f'bt{i}']['balls']:<3} {round(float(data[f'bt{i}']['sr']) if data[f'bt{i}']['sr'] else 0):<3}`"
                )
        
        if batter_data:
            embed.add_field(
                name=f"`{'BATTERS':<24} {'R':<3} {'B':<3} {'SR':<3}`", 
                value="\n".join(batter_data), 
                inline=False
            )

        # Add bowlers info
        bowler_data = []
        for i in range(1, 3):
            if data.get(f'bw{i}') and data[f'bw{i}'].get('name'):
                bowler_data.append(
                    f"`{data[f'bw{i}']['name']:<22} {data[f'bw{i}']['overs']:<4} {data[f'bw{i}']['maiden']:<2} {data[f'bw{i}']['runs']:<3} {data[f'bw{i}']['wkts']}`"
                )
        
        if bowler_data:
            embed.add_field(
                name=f"`{'BOWLERS':<22} {'O':<4} {'M':<2} {'R':<3} W`", 
                value="\n".join(bowler_data), 
                inline=False
            )

        # Cache the result
        self.match_data[url] = embed
        self.match_last_cache[url] = current_time
        return embed

async def setup(bot):
    await bot.add_cog(Scores(bot))