from discord.ext import commands
import discord
import random

NO_MORE_CARDS = "No more cards"


class Deck:
    def __init__(self):
        self.ranks = [
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
            "Ace",
            "Joker",
        ]
        self.suits = ["Spades", "Hearts", "Diamonds", "Clubs"]
        self.cards = []
        self.remaining = 0
        self.user_cards = {}
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

    def deal_card(self, player_name):
        if not self.cards:
            return NO_MORE_CARDS

        self.remaining -= 1
        card = self.cards.pop(0)
        if player_name in self.user_cards:
            self.user_cards[player_name].append(card)
        else:
            self.user_cards[player_name] = [card]
        return card

    def reset_deck(self):
        self.create_deck()
        self.user_cards = {}


class DeckOfCards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.deck = Deck()

    @commands.command(aliases=["init"])
    @commands.bot_has_permissions(manage_messages=True)
    async def dealinitiative(self, ctx):
        """Deal the initiative order for the game.
        The order is based on the card value.
        For example, if the card is "Jack of Hearts", the order will be "Jack of Hearts"
        before "Jack of Diamonds" and "Jack of Clubs" before "Jack of Spades"."""
        await ctx.message.delete()
        players = [member for member in ctx.guild.members if not member.bot]

        initiative_order = {}
        for player in players:
            card = self.deck.deal_card(player.name)
            initiative_order[player.name] = card

        sorted_order = sorted(initiative_order.items(), key=lambda x: x[1])

        embed = self.create_initiative_embed(sorted_order, self.deck.remaining)
        await ctx.send(embed=embed)

    @commands.command(aliases=["rd"])
    @commands.bot_has_permissions(manage_messages=True)
    async def resetdeck(self, ctx):
        """Reset the deck to a full deck."""
        await ctx.message.delete()
        self.deck.reset_deck()
        await self.send_embed(
            ctx,
            "Deck Reset",
            "The deck has been reset to a full deck.",
            discord.Color.yellow(),
        )

    @commands.command(aliases=["dc"])
    @commands.bot_has_permissions(manage_messages=True)
    async def dealcard(self, ctx, player: discord.Member):
        """Deal a card to a user."""
        await ctx.message.delete()
        card = self.deck.deal_card(player.name)
        if card == NO_MORE_CARDS:
            await self.send_embed(
                ctx, "No More Cards", "There are no more cards left in the deck."
            )
        else:
            await self.send_embed(
                ctx, "Card Dealt", f"{player.mention} has been dealt the card: {card}"
            )

    @commands.command(aliases=["sd"])
    @commands.bot_has_permissions(manage_messages=True)
    async def shuffledeck(self, ctx):
        """Shuffle the remaining cards in the deck."""
        await ctx.message.delete()
        random.shuffle(self.deck.cards)
        await self.send_embed(
            ctx,
            "Deck Shuffled",
            "The remaining cards in the deck have been shuffled.",
            discord.Color.yellow(),
        )

    @commands.command(aliases=["sc"])
    @commands.bot_has_permissions(manage_messages=True)
    async def showcards(self, ctx, player: discord.Member):
        """Show the cards a user has."""
        await ctx.message.delete()
        await self.reveal_or_show_cards(ctx, player, reveal=False)

    @commands.command(aliases=["rc"])
    @commands.bot_has_permissions(manage_messages=True)
    async def revealcards(self, ctx, player: discord.Member):
        """Reveal the cards a user has."""
        await ctx.message.delete()
        await self.reveal_or_show_cards(ctx, player, reveal=True)

    @commands.command(aliases=["mc"])
    @commands.bot_has_permissions(manage_messages=True)
    async def mycards(self, ctx):
        """Show the cards of the command user."""
        await ctx.message.delete()
        await self.reveal_or_show_cards(ctx, ctx.author, reveal=False)

    async def send_embed(self, ctx, title, description, color=discord.Color.green()):
        embed = discord.Embed(title=title, color=color, description=description)
        embed.set_footer(text=f"{self.deck.remaining} cards remaining in the deck")
        await ctx.send(embed=embed)

    async def reveal_or_show_cards(self, ctx, player, reveal=False):
        if player.name in self.deck.user_cards:
            cards = self.deck.user_cards[player.name]
            cards_list = "\n".join(cards)
            embed = discord.Embed(
                title="Player Cards",
                description=f"{player.mention} has the following card(s):\n {cards_list}",
            )
        else:
            embed = discord.Embed(
                title="Player Cards",
                description=f"{player.mention} has not been dealt any cards.",
            )

        if reveal:
            await ctx.send(embed=embed)
        else:
            await ctx.author.send(embed=embed)

    def create_initiative_embed(self, sorted_order, remaining):
        embed = discord.Embed(title="Initiative Order", color=discord.Color.blue())
        for index, item in enumerate(sorted_order):
            name = item[0]
            card = item[1]
            embed.add_field(name=f"{index + 1}. {name}", value=card, inline=False)

        embed.set_footer(text=f"{remaining} cards remaining in the deck")
        return embed


async def setup(bot):
    await bot.add_cog(DeckOfCards(bot))
