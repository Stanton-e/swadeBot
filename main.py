from dotenv import load_dotenv
from discord.ext import commands
import discord
import os

import bennies
import deck
import dice
import tokens

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


def delete_message_after_invoke():
    async def predicate(ctx):
        await ctx.message.delete()
        return True

    return commands.check(predicate)


@bot.event
async def on_ready():
    print(f"{bot.user} is now ready!")
    channel = await bot.fetch_channel(CHANNEL_ID)
    if channel:
        await channel.send(f"{bot.user} is now ready!")
    else:
        print("Failed to fetch the specified channel.")


@bot.command()
@delete_message_after_invoke()
async def helpme(ctx):
    command_list = []
    for command in bot.commands:
        command_list.append(command.name)
    commands_string = "\n".join(command_list)
    embed = discord.Embed(title="Available Commands", color=discord.Color.green())
    embed.add_field(name="Commands", value=commands_string, inline=False)
    await ctx.send(embed=embed)


# Add commands from each module
bennies.setup(bot)
deck.setup(bot)
dice.setup(bot)
tokens.setup(bot)


bot.run(TOKEN)
