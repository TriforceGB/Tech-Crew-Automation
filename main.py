# Libraries
import discord
from os import getenv
from dotenv import load_dotenv
import requests
import logging


# Variables
_ = load_dotenv()
TOKEN = getenv('DISCORD_TOKEN')
WEBHOOK = getenv('WEBHOOK')
WEBHOOKTEST = getenv('WEBHOOKTEST')

# Logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Capture all levels

# Create console handler
console_log = logging.StreamHandler()
console_log.setLevel(logging.INFO)  # Show all levels on console

# formates the logs
log_format = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
# Apply formatter to handler
console_log.setFormatter(log_format)
logger.addHandler(console_log)

SeshID = 616754792965865495 # Sesh ID
ChannelID = 1425106319165362246 # Bot Channel

bot = discord.Bot()

# Boot Command
@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name} - {bot.user.id}')

# Scraping new Messaging
@bot.event
async def on_message(message):

    # Only Check messages from Sesh
    if message.author.id == SeshID and message.channel.id == ChannelID:
        logger.info("Starting to Scrape Event: "+message.id)
        # Tactically speaking I could Skip a Node in n8n if I just Pass the Data but IDC
        response =requests.post(f'{WEBHOOK}/scrape', json={'msgID': str(message.id)})

        #logging
        if response.status_code != 200:
            logger.error(f"Failed to scrape message: {message.id}. Status Code: {response.status_code}")

@bot.slash_command(name="help", description="A list of Commands and Links for anything related to Tech Crew")
async def help(
    ctx: discord.ApplicationContext,
    private: discord.Option(bool, "Only Display to You", default=False) # type: ignore
    ):
    logger.info("Sending Help to: "+ctx.user.name)
    embed = discord.Embed(
        title="Tech Crew Help",
        description="This is a List of Commands all Tech Crew Needs",
        color=discord.Colour.blurple() # default color from PyCord
    )
    embed.add_field(name="Links", value="[Discord Server](https://discord.gg/pFBuev6ZWX)\n[Google Classroom](https://classroom.google.com/c/NjM0OTAzNTU3Mzk2)\n[Tech Avengers Event Sheet](https://docs.google.com/spreadsheets/d/18SLwiyRlRUYxtBDuGINRgRQxieXuQJ6Djgq_7UEErCw/edit?usp=sharing)\n[Sesh Website](https://sesh.fyi/dashboard/1374588309317091429)", inline=False)
    embed.add_field(name="Commands", value="`/hours` Get Your Tech Crew Hours\n`/rankings` Get the Top Tech Crew Members\n`/list` Get a List of Upcoming Events\n`/link` Used to Link Sesh with Google Calnder", inline=False)
    embed.add_field(name="Grease the Musical", value="[Musical Classroom](https://classroom.google.com/c/NzczNzExMTkwNTk3)\n[Stage Management Folder](https://drive.google.com/drive/folders/1EvXu2xCEMp3-9KN4YHSnI4dp7P8WxNuh?usp=drive_link) (Includes Cues and Music)\n[Offical Musical Schedule](https://docs.google.com/document/d/1CP6bSJ6qxl60pnh4fp-t30bWnR7JUmCuYKAH0i5By0I/edit?usp=sharing)", inline=False)
    embed.set_thumbnail(url=ctx.guild.icon.url)
    await ctx.respond(embed=embed, ephemeral=private)

@bot.slash_command(name="hours", description="Get Total Tech Crew Hours")
async def hours(
    ctx: discord.ApplicationContext,
    private: discord.Option(bool, "Only Display to You", default=False) # type: ignore
):
    logger.info("Grabing hours for: "+ctx.user.name)
    await ctx.defer(ephemeral=private) # Tell Discord to Chill if this Takes a while
    response = requests.post(f'{WEBHOOK}/command/hours', json={'userID': str(ctx.user.id)}) # Gets the Data from n8n
    if response.ok:
        logger.info("Able to receive hours from n8n")
        data = response.json()
        # format the Data into an Embed

        embed = discord.Embed(
            title=f"🕑 {data['name']}'s Hours",
            color=discord.Colour.fuchsia(), # default color from PyCord
        )
        embed.add_field(name="Overall Hours", value=f"{data['overall']['hours']} - #{data['overall']['rank']}", inline=False)
        embed.add_field(name="Yearly Hours", value=f"{data['yearly']['hours']} - #{data['yearly']['rank']}", inline=False)
        embed.set_thumbnail(url=ctx.user.avatar.url)

        # Send Message
        await ctx.respond(embed=embed,ephemeral=private)

    else:
        logger.error(f"Failed to get hours for {ctx.user.name}. Status Code: {response.status_code}")
        await ctx.respond(f"There was an error getting your hours, status code: {response.status_code}", ephemeral=private)

@bot.slash_command(name="rankings", description="Get Top Tech Crew Members")
async def rankings(
    ctx: discord.ApplicationContext,
    type: discord.Option(str, "Type of Ranking", choices=["Overall", "Yearly"]),
    full: discord.Option(bool, "Show Full Rankings", default=False),
    private: discord.Option(bool, "Only Display to You", default=False) # type: ignore
    ):
    logger.info("Grabing Rankings for: "+ctx.user.name)
    await ctx.defer(ephemeral=private)
    response = requests.post(f'{WEBHOOK}/command/rankings', json={"type": type}) # Gets the Data from n8n
    if response.ok:
        logger.info("Able to receive ranking from n8n")
        data = response.json()
        rankingtext: str = ""
        if full:
            rankingtext += "\n".join([f"{i+1}. <@{member['id']}> - {member['hours']}" for i, member in enumerate(data)])
        else:
            rankingtext += "\n".join([f"{i+1}. <@{member['id']}> - {member['hours']}" for i, member in enumerate(data)][:5])
        embed = discord.Embed(
            title="Tech Crew Rankings",
            description="Top Tech Crew Members",
            color=discord.Color.dark_gold()
        )
        embed.add_field(name=f"{type} Rankings", value=rankingtext, inline=False)
        embed.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.respond(embed=embed,ephemeral=private)
    else:
        logger.error(f"Failed to get rankings for Tech Crew. Status Code: {response.status_code}")
        await ctx.respond(f"There was an error getting the rankings, status code: {response.status_code}", ephemeral=private)
bot.run(TOKEN)
