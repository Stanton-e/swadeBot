from dotenv import load_dotenv
from discord.ext import commands
import discord
import os

load_dotenv()

DEFAULT_BENNY_POOL = int(os.environ["DEFAULT_BENNY_POOL"])
MAIN_CHANNEL_ID = int(os.getenv("MAIN_CHANNEL_ID"))


class BenniesData:
    def __init__(self):
        self.bennies = {"bank": DEFAULT_BENNY_POOL}

    def get_bank_bennies(self):
        return self.bennies["bank"]

    def get_user_bennies(self, user_id):
        return self.bennies.get(str(user_id), 0)

    def give_benny(self, recipient_id, amount):
        if amount <= 0:
            raise ValueError("Amount must be greater than 0.")

        if self.bennies["bank"] < amount:
            raise ValueError("Insufficient bennies in the bank.")

        recipient_bennies = self.get_user_bennies(recipient_id)
        self.bennies["bank"] -= amount
        self.bennies[str(recipient_id)] = recipient_bennies + amount

    def use_benny(self, user_id):
        user_bennies = self.get_user_bennies(user_id)
        if user_bennies <= 0:
            raise ValueError("You don't have any bennies to use.")

        self.bennies["bank"] += 1
        self.bennies[str(user_id)] = user_bennies - 1


class Bennies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bennies_data = BenniesData()

    # Cog-wide check
    async def cog_check(self, ctx):
        # Check if the channel is the main channel
        if ctx.message.channel.id != MAIN_CHANNEL_ID:
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

    @commands.command(aliases=["bb"])
    @commands.is_owner()
    async def benny_balance(self, ctx):
        """Check the current benny balance in the bank."""

        embed = discord.Embed(
            title="Current Benny Balance",
            color=discord.Color.green(),
            description=f"**Bank bennies:** {self.bennies_data.get_bank_bennies()}",
        )
        await ctx.author.send(embed=embed)

    @commands.command(aliases=["bal"])
    async def balance(self, ctx):
        """Check the current benny balance."""

        user_bennies = self.bennies_data.get_user_bennies(ctx.author.id)
        embed = discord.Embed(
            title="Current Benny Balance",
            color=discord.Color.green(),
            description=f"**Your bennies:** {user_bennies}",
        )
        await ctx.author.send(embed=embed)

    @commands.command(aliases=["gb"])
    @commands.is_owner()
    async def give_benny(self, ctx, amount: int, recipient: discord.User):
        """Give a benny or bennies to a user."""

        try:
            self.bennies_data.give_benny(recipient.id, amount)
        except ValueError as e:
            await ctx.send(str(e))
            return

        embed = discord.Embed(
            title=f"Give {'Bennies' if amount > 1 else 'Benny'}",
            color=discord.Color.green(),
            description=f"{ctx.author.mention} has distributed {amount} {'bennies' if amount > 1 else 'benny'} to {recipient.mention}",
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["ub"])
    async def use_benny(self, ctx):
        """Use a benny."""

        try:
            self.bennies_data.use_benny(ctx.author.id)
        except ValueError as e:
            await ctx.send(str(e))
            return

        embed = discord.Embed(
            title="Use Benny",
            description=f"{ctx.author.mention} has used a benny. It goes back to the bank.",
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Bennies(bot))
