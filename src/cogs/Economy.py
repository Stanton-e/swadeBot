from dotenv import load_dotenv
from discord.ext import commands
import discord
import os
import sqlite3

load_dotenv()

CHARACTER_CHANNEL_ID = int(os.environ["CHARACTER_CHANNEL_ID"])


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("swade.db")
        self.cursor = self.conn.cursor()

    # Cog-wide check
    async def cog_check(self, ctx):
        # Check if the channel is the main channel
        if ctx.message.channel.id != CHARACTER_CHANNEL_ID:
            return False

        # Check if the bot has the 'manage_messages' permission in the current channel
        return ctx.channel.permissions_for(ctx.guild.me).manage_messages

    # Listener for all commands
    @commands.Cog.listener()
    async def on_command(self, ctx):
        # Delete the user's command message
        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            pass  # The message is already deleted.
        except discord.errors.Forbidden:
            pass  # Bot doesn't have the required permission to delete the message.

    @commands.command()
    @commands.is_owner()
    async def give_money(self, ctx, user: discord.User, character_name, amount: int):
        # Update the character's money
        self.cursor.execute(
            """
            UPDATE characters
            SET money = money + ?
            WHERE user_id = ? AND name = ? COLLATE NOCASE
            """,
            (amount, str(user.id), character_name),
        )

        self.conn.commit()

        if self.cursor.rowcount == 0:
            await ctx.author.send(
                f"{user.name} doesn't have a character named {character_name}."
            )
            return

        await ctx.author.send(
            f"Gave {amount} money to {character_name} belonging to {user.name}."
        )

    @commands.command()
    @commands.is_owner()
    async def take_money(self, ctx, user: discord.User, character_name, amount: int):
        # Get the character's money
        self.cursor.execute(
            """
            SELECT money FROM characters
            WHERE user_id = ? AND name = ? COLLATE NOCASE
            """,
            (str(user.id), character_name),
        )
        result = self.cursor.fetchone()

        if result is None:
            await ctx.author.send(
                f"{user.name} doesn't have a character named {character_name}."
            )
            return

        if result[0] < amount:
            await ctx.author.send(
                f"{character_name} belonging to {user.name} doesn't have enough money."
            )
            return

        # If the character has enough money, subtract the amount from the character's money
        self.cursor.execute(
            """
            UPDATE characters
            SET money = money - ?
            WHERE user_id = ? AND name = ? COLLATE NOCASE
            """,
            (amount, str(user.id), character_name),
        )

        self.conn.commit()

        await ctx.author.send(
            f"Took {amount} money from {character_name} belonging to {user.name}."
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
