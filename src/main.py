from dotenv import load_dotenv
from discord.ext import commands
import asyncio
import discord
import json
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
MAIN_CHANNEL_ID = int(os.getenv("MAIN_CHANNEL_ID"))
OWNER_IDS_STR = os.getenv("OWNER_IDS")
OWNER_IDS = json.loads(OWNER_IDS_STR)

intents = discord.Intents.all()


# Custom Help command
class CustomHelpCommand(commands.DefaultHelpCommand):
    async def send_command_help(self, command):
        ctx = self.context
        if await command.can_run(ctx):
            await super().send_command_help(command)

    async def send_cog_help(self, cog):
        filtered = commands.CommandCog(commands=self)
        for command in cog.get_commands():
            if await command.can_run(self.context):
                filtered.add_command(command)
        await super().send_cog_help(filtered)


bot = commands.Bot(
    command_prefix="!",
    owner_ids=set(OWNER_IDS),
    intents=intents,
    help_command=CustomHelpCommand(),
)


async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            cog_name = filename[:-3]
            cog = getattr(__import__(f"cogs.{cog_name}", fromlist=["cogs"]), cog_name)
            cog_instance = cog(bot)
            await bot.add_cog(cog_instance)
            print(f"Loaded extension: {cog_name}")


@bot.event
async def on_ready():
    print(f"{bot.user} is now ready!")
    channel = bot.get_channel(MAIN_CHANNEL_ID)
    if channel:
        await channel.send(f"{bot.user} is now ready!")
    else:
        print("Failed to fetch the specified channel.")


async def main():
    await load_cogs()
    await bot.start(TOKEN)


asyncio.run(main())
