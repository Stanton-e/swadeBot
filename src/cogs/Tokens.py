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

    async def cog_check(self, ctx):
        return (
            ctx.channel.id == MAIN_CHANNEL_ID
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

    @commands.command(aliases=["gt"])
    @commands.has_role("GameMaster")
    async def give_token(
        self,
        ctx,
        player: discord.Member = commands.parameter(
            description="User ID from whom to add the token."
        ),
        token: str = commands.parameter(description="Token name in which to add."),
    ):
        """
        Description: Give tokens to user.

        Params:
        !gt UserID NameOfToken

        Example:
        !gt 1234567890 Defend
        """

        if token not in TOKENS:
            await ctx.send(f"Invalid token. Available tokens: {', '.join(TOKENS)}")
            return

        if player.id not in self.players:
            self.players[player.id] = Player(player)

        self.players[player.id].add_token(token)
        await ctx.send(f"{player.mention} has been given the {token} token.")

    @commands.command(aliases=["rt"])
    @commands.has_role("GameMaster")
    async def remove_token(
        self,
        ctx,
        player: discord.Member = commands.parameter(
            description="User ID from whom to remove the token."
        ),
        token: str = commands.parameter(description="Token name in which to remove."),
    ):
        """
        Description: Remove a token from user.

        Params:
        !rt UserID NameOfToken

        Example:
        !rt 1234567890 Defend
        """

        if token not in TOKENS:
            await ctx.send(f"Invalid token. Available tokens: {', '.join(TOKENS)}")
            return

        if player.id in self.players and token in self.players[player.id].tokens:
            self.players[player.id].remove_token(token)
            await ctx.send(f"{player.mention} no longer has the {token} token.")
        else:
            await ctx.send(f"{player.mention} has no tokens.")

    @commands.command(aliases=["ct"])
    @commands.has_role("GameMaster")
    async def clear_tokens(
        self,
        ctx,
        player: discord.Member = commands.parameter(
            description="User ID from whom to clear tokens."
        ),
    ):
        """
        Description: Clear all tokens from user.

        Params:
        !ct UserID

        Example:
        !ct 1234567890
        """

        if player.id in self.players:
            self.players[player.id].clear_tokens()
            await ctx.send(f"All tokens have been cleared for {player.mention}.")

    @commands.command(aliases=["st"])
    @commands.has_role("GameMaster")
    async def show_tokens(
        self,
        ctx,
        player: discord.Member = commands.parameter(
            description="User ID from whom to show all tokens."
        ),
    ):
        """
        Description: Show tokens from user.

        Params:
        !st UserID

        Example:
        !st 1234567890
        """

        if player.id in self.players and self.players[player.id].tokens:
            tokens_string = ", ".join(self.players[player.id].tokens)
            await ctx.send(f"{player.mention} tokens: {tokens_string}")
        else:
            await ctx.send(f"{player.mention} has no tokens.")

    @commands.command(aliases=["vt"])
    async def view_tokens(self, ctx):
        """
        Description: View user tokens.

        Params:
        !vt UserID

        Example:
        !vt 1234567890
        """

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
