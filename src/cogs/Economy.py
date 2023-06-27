from dotenv import load_dotenv
from discord.ext import commands
from models.MoneyModel import Money
import discord
import os

load_dotenv()

CHARACTER_CHANNEL_ID = int(os.environ["CHARACTER_CHANNEL_ID"])


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.money = Money()

    async def cog_check(self, ctx):
        return (
            ctx.channel.id == CHARACTER_CHANNEL_ID
            and ctx.guild.me.guild_permissions.manage_messages
        )

    @commands.Cog.listener()
    async def on_command(self, ctx):
        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            pass  # The message is already deleted.
        except discord.errors.Forbidden:
            pass  # Bot doesn't have the required permission to delete the message.

    @commands.command()
    @commands.has_role("GameMaster")
    async def give_money(self, ctx, player: discord.User, character_name, amount: int):
        character = self.money.read(player.id, character_name)

        if character is None:
            await ctx.author.send(
                f"{player.name} doesn't have a character named {character_name}."
            )
            return

        self.money.add(player.id, character_name, amount)

        await ctx.author.send(
            f"Gave {amount} money to {character_name} belonging to {player.name}."
        )

    @commands.command()
    @commands.has_role("GameMaster")
    async def take_money(self, ctx, player: discord.User, character_name, amount: int):
        result = self.money.read(player.id, character_name)

        if result is None:
            await ctx.author.send(
                f"{player.name} doesn't have a character named {character_name}."
            )
            return

        if result[0] < amount:
            await ctx.author.send(
                f"{character_name} belonging to {player.name} doesn't have enough money."
            )
            return

        self.money.subtract(player.id, character_name, amount)

        await ctx.author.send(
            f"Took {amount} money from {character_name} belonging to {player.name}."
        )

    @give_money.error
    @take_money.error
    async def command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.author.send(
                "You must specify a user, character name, and amount of money to give or take."
            )


async def setup(bot):
    await bot.add_cog(Economy(bot))
