from discord.ext import commands

class CommandsCog(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @commands.command()
    async def another_command(self, ctx):
        # Add logic for another command
        await ctx.send("Another command executed!")

def setup(bot):
    bot.add_cog(CommandsCog(bot))
