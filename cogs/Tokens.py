from dotenv import load_dotenv
from discord.ext import commands
import discord
import os

load_dotenv()

MAIN_CHANNEL_ID = int(os.getenv("MAIN_CHANNEL_ID"))
TOKENS = [
    "Shaken",
    "Aim",
    "Entangled",
    "Wounded",
    "Bound",
    "Fatigue",
    "Stunned",
    "Vulnerable",
    "Defend",
    "Hold",
    "Distracted",
]


class Player:
    def __init__(self, member):
        self.member = member
        self.tokens = []

    def add_token(self, token):
        if token not in self.tokens:
            self.tokens.append(token)

    def remove_token(self, token):
        if token in self.tokens:
            self.tokens.remove(token)

    def clear_tokens(self):
        self.tokens = []


class Tokens(commands.Cog):
    def cog_check(self, ctx):
        return ctx.message.channel.id == MAIN_CHANNEL_ID

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    @commands.command(aliases=["gt"])
    @commands.is_owner()
    @commands.bot_has_permissions(manage_messages=True)
    async def givetoken(self, ctx, player: discord.Member, token: str):
        """Give a token or tokens to a user."""
        await ctx.message.delete()

        if token not in TOKENS:
            await ctx.send(f"Invalid token. Available tokens: {', '.join(TOKENS)}")
            return

        if player.id not in self.players:
            self.players[player.id] = Player(player)

        self.players[player.id].add_token(token)
        await ctx.send(f"{player.mention} has been given the {token} token.")

    @commands.command(aliases=["rt"])
    @commands.is_owner()
    @commands.bot_has_permissions(manage_messages=True)
    async def removetoken(self, ctx, player: discord.Member, token: str):
        """Remove a token from a user."""
        await ctx.message.delete()

        if token not in TOKENS:
            await ctx.send(f"Invalid token. Available tokens: {', '.join(TOKENS)}")
            return

        if player.id in self.players and token in self.players[player.id].tokens:
            self.players[player.id].remove_token(token)
            await ctx.send(f"{player.mention} no longer has the {token} token.")
        else:
            await ctx.send(f"{player.mention} has no tokens.")

    @commands.command(aliases=["ct"])
    @commands.is_owner()
    @commands.bot_has_permissions(manage_messages=True)
    async def cleartokens(self, ctx, player: discord.Member):
        """Clear all tokens from a user."""
        await ctx.message.delete()

        if player.id in self.players:
            self.players[player.id].clear_tokens()
            await ctx.send(f"All tokens have been cleared for {player.mention}.")

    @commands.command(aliases=["st"])
    @commands.is_owner()
    @commands.bot_has_permissions(manage_messages=True)
    async def showtokens(self, ctx, player: discord.Member):
        """Show all tokens from a user."""
        await ctx.message.delete()

        if player.id in self.players and self.players[player.id].tokens:
            tokens_string = ", ".join(self.players[player.id].tokens)
            await ctx.send(f"{player.mention} tokens: {tokens_string}")
        else:
            await ctx.send(f"{player.mention} has no tokens.")

    @commands.command(aliases=["vt"])
    @commands.bot_has_permissions(manage_messages=True)
    async def viewtokens(self, ctx):
        """Show all your tokens."""
        await ctx.message.delete()

        if ctx.author.id in self.players and self.players[ctx.author.id].tokens:
            tokens_string = ", ".join(self.players[ctx.author.id].tokens)
            await ctx.author.send(f"{ctx.author.mention} tokens: {tokens_string}")
        else:
            await ctx.author.send(f"{ctx.author.mention} has no tokens.")

    @givetoken.error
    async def givetoken_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a user.")

    @showtokens.error
    async def showtokens_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a user.")

    @cleartokens.error
    async def cleartokens_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a user.")

    @removetoken.error
    async def removetoken_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a user and token.")


async def setup(bot):
    await bot.add_cog(Tokens(bot))
