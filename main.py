# Libraries
import discord
from discord.ext import commands
from os import getenv
from dotenv import load_dotenv
import requests


# Variables
load_dotenv()
TOKEN = getenv('DISCORD_TOKEN')
EVENTWEBHOOK = getenv('EVENT_WEBHOOK')
SLASHWEBHOOK = getenv('SLASH_WEBHOOK')

SeshID = 616754792965865495 # Sesh ID
ChannelID = 1425106319165362246 # Bot Channel

# the Intent for the Bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.webhooks = True

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    
# Scraping new Messaging
@bot.event
async def on_message(message):
    # Only Check messages from Sesh
    if message.author.id == SeshID and message.channel.id == ChannelID:
        print(message.id)
        # Tactically speaking I could Skip a Node in n8n if I just Pass the Data but IDC
        requests.post(EVENTWEBHOOK, json={'msgID': str(message.id)})
        


@bot.slash_command(name="hours", description="Get Total Tech Crew Hours")
async def hours(
    ctx: discord.ApplicationContext,
    private: discord.Option(bool, "Only Display to You", default=False) # type: ignore
):
    # await requests.get(SLASHWEBHOOK, json={'command': "personalHours"})
    await ctx.respond("Hey!", ephemeral=private)

@bot.slash_command(name="rankings", description="Get Top Tech Crew Members")
async def hours(ctx: discord.ApplicationContext):
    await ctx.respond("Hey!")
bot.run(TOKEN)