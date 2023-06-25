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
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

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

    @commands.command(aliases=["gt"])
    @commands.is_owner()
    async def give_token(self, ctx, player: discord.Member, token: str):
        """Give a token or tokens to a user."""

        if token not in TOKENS:
            await ctx.send(f"Invalid token. Available tokens: {', '.join(TOKENS)}")
            return

        if player.id not in self.players:
            self.players[player.id] = Player(player)

        self.players[player.id].add_token(token)
        await ctx.send(f"{player.mention} has been given the {token} token.")

    @commands.command(aliases=["rt"])
    @commands.is_owner()
    async def remove_token(self, ctx, player: discord.Member, token: str):
        """Remove a token from a user."""

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
    async def clear_tokens(self, ctx, player: discord.Member):
        """Clear all tokens from a user."""

        if player.id in self.players:
            self.players[player.id].clear_tokens()
            await ctx.send(f"All tokens have been cleared for {player.mention}.")

    @commands.command(aliases=["st"])
    @commands.is_owner()
    async def show_tokens(self, ctx, player: discord.Member):
        """Show all tokens from a user."""

        if player.id in self.players and self.players[player.id].tokens:
            tokens_string = ", ".join(self.players[player.id].tokens)
            await ctx.send(f"{player.mention} tokens: {tokens_string}")
        else:
            await ctx.send(f"{player.mention} has no tokens.")

    @commands.command(aliases=["vt"])
    async def view_tokens(self, ctx):
        """Show all your tokens."""

        if ctx.author.id in self.players and self.players[ctx.author.id].tokens:
            tokens_string = ", ".join(self.players[ctx.author.id].tokens)
            await ctx.author.send(f"{ctx.author.mention} tokens: {tokens_string}")
        else:
            await ctx.author.send(f"{ctx.author.mention} has no tokens.")

    @give_token.error
    @show_tokens.error
    @clear_tokens.error
    @remove_token.error
    async def command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Missing argument. Please check the command syntax and try again."
            )


async def setup(bot):
    await bot.add_cog(Tokens(bot))
