import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

extensions = ['scores']

# Bot Setup
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Load Cogs
@bot.before_invoke
async def before_command(ctx):
    print(f"Command '{ctx.command}' is being invoked.")

for extension in extensions:
    extensions(extension) 
    print('Loaded Extension: ', extension)

# Run the bot
bot.run(TOKEN)
