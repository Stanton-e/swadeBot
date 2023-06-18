from discord.ext import commands
import discord


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


players = {}


def delete_message_after_invoke():
    async def predicate(ctx):
        await ctx.message.delete()
        return True

    return commands.check(predicate)


def setup(bot):
    @bot.command(aliases=["gt"])
    @delete_message_after_invoke()
    async def givetoken(ctx, player: discord.Member, token: str):
        if token not in TOKENS:
            await ctx.send(f"Invalid token. Available tokens: {', '.join(TOKENS)}")
            return

        if player.id not in players:
            players[player.id] = Player(player)

        players[player.id].add_token(token)
        await ctx.send(f"{player.mention} has been given the {token} token.")

    @bot.command(aliases=["rt"])
    @delete_message_after_invoke()
    async def removetoken(ctx, player: discord.Member, token: str):
        if token not in TOKENS:
            await ctx.send(f"Invalid token. Available tokens: {', '.join(TOKENS)}")
            return

        if player.id in players:
            players[player.id].remove_token(token)
            await ctx.send(f"{player.mention} no longer has the {token} token.")

    @bot.command(aliases=["ct"])
    @delete_message_after_invoke()
    async def cleartokens(ctx, player: discord.Member):
        if player.id in players:
            players[player.id].clear_tokens()
            await ctx.send(f"All tokens have been cleared for {player.mention}.")

    @bot.command(aliases=["st"])
    @delete_message_after_invoke()
    async def showtokens(ctx, player: discord.Member):
        if player.id in players:
            player_tokens = players[player.id].tokens
            if player_tokens:
                tokens_string = ", ".join(player_tokens)
                await ctx.send(f"{player.mention} tokens: {tokens_string}")
            else:
                await ctx.send(f"{player.mention} has no tokens.")
        else:
            await ctx.send(f"{player.mention} has no tokens.")
