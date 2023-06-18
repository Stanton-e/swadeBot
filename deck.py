from discord.ext import commands
import discord
import random


class Deck:
    def __init__(self):
        self.ranks = [
            "Joker",
            "Ace",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "Jack",
            "Queen",
            "King",
        ]
        self.suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        self.cards = []
        self.remaining = 0

        self.create_deck()

    def create_deck(self):
        self.cards = []
        for rank in self.ranks:
            if rank == "Joker":
                self.cards.extend([rank, rank])  # Add two Joker cards
            else:
                for suit in self.suits:
                    self.cards.append(f"{rank} of {suit}")
        self.remaining = len(self.cards)
        random.shuffle(self.cards)

    def deal_card(self):
        if not self.cards:
            return "No more cards"

        self.remaining -= 1
        return self.cards.pop(0)

    def reset_deck(self):
        self.create_deck()


def delete_message_after_invoke():
    async def predicate(ctx):
        await ctx.message.delete()
        return True

    return commands.check(predicate)


def create_initiative_embed(sorted_order, remaining):
    embed = discord.Embed(title="Initiative Order", color=discord.Color.blue())
    for index, item in enumerate(sorted_order):
        name = item[0]
        card = item[1]
        embed.add_field(name=f"{index + 1}. {name}", value=card, inline=False)

    embed.set_footer(text=f"{remaining} cards remaining in the deck")
    return embed


def setup(bot):
    deck = Deck()

    @bot.command(aliases=["init"])
    @delete_message_after_invoke()
    async def dealinitiative(ctx):
        players = [member for member in ctx.guild.members if not member.bot]

        initiative_order = {}
        for player in players:
            card = deck.deal_card()
            initiative_order[player.name] = card

        sorted_order = sorted(initiative_order.items(), key=lambda x: x[1])

        embed = create_initiative_embed(sorted_order, deck.remaining)
        await ctx.send(embed=embed)

    @bot.command(aliases=["rd"])
    @delete_message_after_invoke()
    async def resetdeck(ctx):
        deck.reset_deck()
        embed = discord.Embed(
            title="Deck Reset",
            color=discord.Color.yellow(),
            description=f"The deck has been reset to a full deck.",
        )
        embed.set_footer(text=f"{deck.remaining} cards remaining in the deck")
        await ctx.send(embed=embed)

    @bot.command(aliases=["dc"])
    @delete_message_after_invoke()
    async def dealcard(ctx, player: discord.Member):
        card = deck.deal_card()
        if card == "No more cards":
            embed = discord.Embed(
                title="No More Cards",
                description="There are no more cards left in the deck.",
            )
        else:
            embed = discord.Embed(
                title="Card Dealt",
                description=f"{player.mention} has been dealt the card: {card}",
            )

        embed.set_footer(text=f"{deck.remaining} cards remaining in the deck")
        await ctx.send(embed=embed)

    @bot.command(aliases=["sd"])
    @delete_message_after_invoke()
    async def shuffledeck(ctx):
        random.shuffle(deck.cards)
        embed = discord.Embed(
            title="Deck Shuffled",
            color=discord.Color.yellow(),
            description=f"The remaining cards in the deck have been shuffled.",
        )
        embed.set_footer(text=f"{deck.remaining} cards remaining in the deck")
        await ctx.send(embed=embed)

    @bot.command(aliases=["show"])
    @delete_message_after_invoke()
    async def showdeck(ctx):
        embed = discord.Embed(title="Current Deck", color=discord.Color.green())
        cards_string = "\n".join(deck.cards)
        embed.add_field(name="Cards", value=cards_string, inline=False)
        embed.set_footer(text=f"{deck.remaining} cards remaining in the deck")
        await ctx.send(embed=embed)
