from dotenv import load_dotenv
from discord.ext import commands
import discord
import os

load_dotenv()

DEFAULT_BENNY_POOL = int(os.environ["DEFAULT_BENNY_POOL"])


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

    @commands.command(aliases=["bb"])
    @commands.is_owner()
    @commands.bot_has_permissions(manage_messages=True)
    async def bennybalance(self, ctx):
        """Check the current benny balance in the bank."""
        await ctx.message.delete()

        embed = discord.Embed(
            title="Current Benny Balance",
            color=discord.Color.green(),
            description=f"**Bank bennies:** {self.bennies_data.get_bank_bennies()}",
        )
        await ctx.author.send(embed=embed)

    @commands.command(aliases=["bal"])
    @commands.bot_has_permissions(manage_messages=True)
    async def balance(self, ctx):
        """Check the current benny balance in your bank."""
        await ctx.message.delete()

        user_bennies = self.bennies_data.get_user_bennies(ctx.author.id)
        embed = discord.Embed(
            title="Current Benny Balance",
            color=discord.Color.green(),
            description=f"**Your bennies:** {user_bennies}",
        )
        await ctx.author.send(embed=embed)

    @commands.command(aliases=["gb"])
    @commands.is_owner()
    @commands.bot_has_permissions(manage_messages=True)
    async def givebenny(self, ctx, amount: int, recipient: discord.User):
        """Give a benny or bennies to a user."""
        await ctx.message.delete()

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
    @commands.bot_has_permissions(manage_messages=True)
    async def usebenny(self, ctx):
        """Use a benny."""
        await ctx.message.delete()

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
