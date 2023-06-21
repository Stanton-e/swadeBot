from dotenv import load_dotenv
from discord.ext import commands
import asyncio
import discord
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
OWNER_IDS = [90681659204046848,792819767064395797]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = "!", owner_ids = set(OWNER_IDS), intents = intents, help_command = commands.DefaultHelpCommand())  # Use the in-built help command
@commands.bot_has_permissions(manage_messages=True)


async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded extension: {filename[:-3]}")
            except Exception as e:
                print(f"Failed to load extension: {filename[:-3]}.\n{type(e).__name__}: {e}")


@bot.event
async def on_ready():
    print(f"{bot.user} is now ready!")
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(f"{bot.user} is now ready!")
    else:
        print("Failed to fetch the specified channel.")


async def main():
    await load_cogs()
    await bot.start(TOKEN)


asyncio.run(main())
