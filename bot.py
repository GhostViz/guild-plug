from configs import redis_conf, discord_conf
import discord, caching, json, utility
from discord.ext import commands
from discord import Interaction

r = redis_conf.r

def run_discord_bot():
    TOKEN = discord_conf.TOKEN
    intents = discord.Intents.all()
    intents.message_content = True
    client = commands.Bot( command_prefix='.', description='Retrieves guild roster information as json output from battle.net\'s world of warcraft profile api and caches it to redis', intents=intents)

    @client.event
    async def on_ready():
        await client.tree.sync()
        await client.change_presence(activity=discord.activity.Game(name="World of Warcraft"))
        print( f'{ client.user.name } just showed up!' )

    @client.tree.command(name="ping", description="show ping")
    async def ping( interaction : Interaction ):
        bot_latency = round( client.latency*1000 )
        await interaction.response.send_message(f"Pong!... {bot_latency} ms")

    @client.tree.command(name="roll", description="roll a die with 'd' sides")
    async def roll( interaction : Interaction, d: int ):
        await interaction.response.send_message( f"{ interaction.user } rolled a d{ d } and got a { utility.roll( d ) }" )

    @client.tree.command(name="update_guild_roster", description="updates the cached information for a guild roster")
    async def update_guild_roster( interaction : Interaction, guild_realm: str, guild_slug: str ):
        await interaction.response.send_message(caching.guild_roster_update( 'us', 'en_us', guild_slug, guild_realm ))

    # Needs to be implemented in a non-blocking way
    # @client.tree.command(name="update_guild_professions", description="updates the cached information for the professions of an entire guild.")
    # async def update_guild_professions( interaction : Interaction, guild_realm: str, guild_slug: str ):
    #     guild_roster = json.loads( r.get( guild_slug + "_" + guild_realm ).decode( 'ascii' ) ).get( "members" )
    #     await interaction.response.send_message(caching.guild_roster_character_professions_update( guild_roster, guild_slug, guild_realm ))    

    client.run(TOKEN)