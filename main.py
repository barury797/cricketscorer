import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Bot Setup
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=("c. ", "C. ", "c.", "C."), intents=intents, case_insensitive=True)
extensions = ['cog_general', 'match_score.cog_scores', 'cricket_guru.cog_cgstats']

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    
    # Load all extensions
    try:
        for extension in extensions:
            await bot.load_extension(extension)
        print("Loaded all extensions")
    except Exception as e:
        print(f"Failed to load extension {extension}: {e}")

@bot.before_invoke
async def before_command(ctx):
    print(f"Command '{ctx.command}' is being invoked.")    

# Handle Command Errors
@bot.event
async def on_command_error(ctx, error):
    # If it's a command not found error
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Sorry, that command doesn't exist!")
    # If it's a missing argument error
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument: {error}")
    # Handle all other errors
    else:
        await ctx.send(f"An error occurred: {error}")
        raise error  # Re-raise to log it

# Run the bot
bot.run(TOKEN)