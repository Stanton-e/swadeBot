from dotenv import load_dotenv
from discord.ext import commands
from models.EncounterModel import Encounter
import discord
import os
import random

load_dotenv()

MAIN_CHANNEL_ID = int(os.getenv("MAIN_CHANNEL_ID"))
NO_MORE_CARDS = "No more cards"


class Player:
    def __init__(self, name, health, monster=False):
        self.name = name
        self.health = health
        self.monster = monster
        self.cards = []
        self.card_values = []

    def get_cards(self):
        return ", ".join(self.cards)

    def deal_card(self, card, card_value):
        self.cards.append(card)
        self.card_values.append(card_value)


class Deck:
    def __init__(self):
        self.ranks = [
            "Joker",
            "Ace",
            "King",
            "Queen",
            "Jack",
            "10",
            "9",
            "8",
            "7",
            "6",
            "5",
            "4",
            "3",
            "2",
        ]
        self.ranks_value = {
            "Joker": 15,
            "Ace": 14,
            "King": 13,
            "Queen": 12,
            "Jack": 11,
            "10": 10,
            "9": 9,
            "8": 8,
            "7": 7,
            "6": 6,
            "5": 5,
            "4": 4,
            "3": 3,
            "2": 2,
        }
        self.suits = ["Spades", "Hearts", "Diamonds", "Clubs"]
        self.suits_value = {"Spades": 4, "Hearts": 3, "Diamonds": 2, "Clubs": 1}
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

    def deal_card(self, player):
        if not self.cards:
            raise NoMoreCardsError("No more cards in the deck.")

        self.remaining -= 1
        card = self.cards.pop(0)
        card_value = self.get_card_value(card)
        player.deal_card(card, card_value)

    def reset_deck(self):
        self.create_deck()
        self.user_cards = {}
        for player in self.players:
            player.cards = []
            player.card_values = []

    def get_card_value(self, card):
        if card == "Joker":
            return (5, 15)  # Joker is the highest value card.

        rank, suit = card.split(" of ")
        return (self.suits_value[suit], self.ranks_value[rank])


class NoMoreCardsError(Exception):
    """Raised when there are no more cards in the deck."""

    pass


class DeckOfCards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.deck = Deck()
        self.current_turn = 0
        self.initiative_order = []
        self.encounter = Encounter()

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

    @commands.command(aliases=["di", "init"])
    @commands.has_role("GameMaster")
    async def deal_initiative(self, ctx, encounter_id):
        """Deal the initiative order for the game. The order is based on the card value."""
        # Look up the characters and monsters for the given encounter.
        characters_data, monsters_data = self.encounter.initiative(encounter_id)

        # Create Player objects for characters and monsters.
        characters = [Player(row[0], row[1]) for row in characters_data]
        monsters = [Player(row[0], row[1], monster=True) for row in monsters_data]

        # Add characters and monsters to the deck's list of players.
        self.deck.players = characters + monsters

        # Deal cards to each player.
        for player in self.deck.players:
            try:
                self.deck.deal_card(player)
            except Exception as e:
                await ctx.send(str(e))

        # Sort the initiative order by card value.
        self.deck.players.sort(key=lambda player: player.card_values[-1], reverse=True)

        # Send the initiative order as an embed.
        embed = self.create_initiative_embed()
        await ctx.send(embed=embed)

        # Send the current player embed
        current_player_embed = self.create_current_player_embed(self.deck.players[0])
        await ctx.send(embed=current_player_embed)

    @commands.command(aliases=["ei", "end"])
    @commands.has_role("GameMaster")
    async def end_initiative(self, ctx):
        """End the initiative order and reset deck."""
        try:
            self.initiative_order = []
            self.current_turn = 0  # Reset current turn
            self.deck.reset_deck()

            await self.send_embed(
                ctx,
                "Encounter Ended",
                "The Encounter has ended and the deck has been reset to a full deck.",
                discord.Color.blue(),
            )
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.command(aliases=["dc", "deal"])
    @commands.has_role("GameMaster")
    async def deal_card(self, ctx, player_name):
        """Deal a card to the specified player."""
        player = next(
            (player for player in self.deck.players if player.name == player_name), None
        )
        if player:
            try:
                self.deck.deal_card(player)
                await ctx.send(f"A card was dealt to {player.name}.")
            except NoMoreCardsError as e:
                await ctx.send(f"No more cards: {str(e)}")
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")
        else:
            await ctx.send("Player not found.")

    @commands.command(aliases=["vpc"])
    @commands.has_role("GameMaster")
    async def view_player_cards(self, ctx, player_name):
        """View the cards of the specified player."""
        player = next(
            (player for player in self.deck.players if player.name == player_name), None
        )
        if player:
            cards = player.get_cards()
            await ctx.author.send(f"{player.name}'s cards: {cards}")
        else:
            await ctx.send("Player not found.")

    @commands.command(aliases=["rh", "reveal"])
    async def reveal_hand(self, ctx, player_name=None):
        """Reveal your hand or the hand of the specified player."""
        if player_name is None:
            player_name = ctx.author.name
        player = next(
            (player for player in self.deck.players if player.name == player_name), None
        )
        if player:
            cards = player.get_cards()
            await ctx.send(f"{player.name} reveals their hand: {cards}")
        else:
            await ctx.send("Player not found.")

    @commands.command(aliases=["n", "nt"])
    @commands.has_role("GameMaster")
    async def next_turn(self, ctx):
        self.current_turn = (self.current_turn + 1) % len(self.deck.players)

        # Send the current player embed
        current_player = self.deck.players[self.current_turn]
        current_player_embed = self.create_current_player_embed(current_player)
        await ctx.send(embed=current_player_embed)

    def create_current_player_embed(self, player):
        color = discord.Color.red() if player.monster else discord.Color.green()
        embed = discord.Embed(title="Current Player", color=color)
        embed.add_field(
            name=f"{player.name}'s Turn",
            value=f"Health: {player.health}",
            inline=False,
        )
        return embed

    async def send_embed(self, ctx, title, description, color=discord.Color.green()):
        embed = discord.Embed(title=title, color=color, description=description)
        embed.set_footer(text=f"{self.deck.remaining} cards remaining in the deck")
        await ctx.send(embed=embed)

    def create_initiative_embed(self):
        embed = discord.Embed(title="Initiative Order", color=discord.Color.blue())
        for i, player in enumerate(self.deck.players, start=1):
            name = f"{i}. {player.name}"
            embed.add_field(name=name, value=player.cards[-1], inline=False)
        embed.set_footer(text=f"{len(self.deck.cards)} cards remaining in the deck")
        return embed


async def setup(bot):
    await bot.add_cog(DeckOfCards(bot))
