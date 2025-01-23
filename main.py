import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Bot Setup
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="c.", intents=intents)
extensions = ['cog_general', 'cog_scores']

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await load_extensions()  # Load extensions here after bot is ready

@bot.before_invoke
async def before_command(ctx):
    print(f"Command '{ctx.command}' is being invoked.")

# Load Cogs with Error Handling
async def load_extensions():
    for extension in extensions:
        try:
            await bot.load_extension(extension)
            print(f"Loaded extension {extension}")
        except Exception as e:
            print(f"Failed to load extension {extension}: {e}")

# Handle Command Errors
@bot.event
async def on_command_error(ctx, error):
    # If it's a command not found error
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Sorry, that command doesn't exist!")
    # If it's a missing argument error
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument: {error.param}")
    # Handle all other errors
    else:
        await ctx.send(f"An error occurred: {error}")
        raise error  # Re-raise to log it

# Run the bot
bot.run(TOKEN)