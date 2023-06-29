from dotenv import load_dotenv
from discord.ext import commands
from models.ItemModel import Item
import discord
import os

load_dotenv()

MARKET_CHANNEL_ID = int(os.environ["MARKET_CHANNEL_ID"])


class Store(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.item = Item()

    async def cog_check(self, ctx):
        return (
            ctx.channel.id == MARKET_CHANNEL_ID
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

    @commands.command()
    @commands.has_role("GameMaster")
    async def add_item(
        self,
        ctx,
        item_name: str = commands.parameter(description="Name of item."),
        category: str = commands.parameter(description="Name of category."),
        price: int = commands.parameter(description="Cost of item."),
    ):
        """
        Description: Add item to store.

        Params:
        !add_item NameOfItem NameOfCategory Price

        Example:
        !add_item Machete Weapons 25
        """

        if price <= 0:
            await ctx.send("Value must be a positive integer.")
            return

        new_item = (item_name, category, price)

        self.item.insert(new_item)

        await ctx.send(f"Added **{item_name}** to the store with a value of {price}.")

    @commands.command()
    @commands.has_role("GameMaster")
    async def remove_item(
        self,
        ctx,
        item_id: int = commands.parameter(description="ID of item."),
        item_name: str = commands.parameter(description="Name of item."),
    ):
        """
        Description: Delete an item from store.

        Params:
        !delete_item ItemID NameOfItem

        Example:
        !delete_item 1 Machete
        """

        self.item.delete(item_id, item_name)

        await ctx.send(f"Removed **{item_name}** from the store.")

    @commands.command()
    async def view_items(self, ctx):
        """
        Description: View items in store.

        Params:
        N/A

        Example:
        !view_items
        """

        items = self.item.read_all()

        if not items:
            await ctx.send("The store is currently empty.")
            return

        message = "Items available in the store:\n"
        for item in items:
            message += f"**{item[1]}:** {item[3]}\n"

        await ctx.send(message)

    @commands.command()
    async def buy_item(
        self,
        ctx,
        character_name: str = commands.parameter(description="Name of character."),
        item_name: str = commands.parameter(description="Name of item."),
        quantity: int = commands.parameter(description="Quantity to buy", default=1),
    ):
        """
        Description: Buy an item from store.

        Params:
        !buy_item NameOfItem Quantity

        Example:
        !buy_item Machete 1
        """

        if quantity <= 0:
            await ctx.send("Quantity must be a positive integer.")
            return

        if quantity > 100:
            await ctx.send("You cannot buy more than 100 of the same item.")
            return

        data = self.item.read(item_name)

        if data is None:
            await ctx.send(f"The item **{item_name}** does not exist in the store.")
            return

        value = data[3] * quantity
        result = self.item.buy(str(ctx.author.id), character_name)

        if result is None:
            await ctx.send(f"You don't have a character named **{character_name}**.")
            return

        if result[0] < value:
            await ctx.send(
                f"Your character **{character_name}** does not have enough money to buy this item."
            )
            return

        item_counts = {}
        if result[1]:
            # Parse the existing equipment string into a dictionary
            items = result[1].split(",")
            for item in items:
                item = item.strip()
                name, count = item.split(":")
                item_counts[name] = int(count)

        item_count = item_counts.get(item_name, 0)
        if item_count + quantity > 100:
            await ctx.send(
                f"You already have {item_count} unit(s) of **{item_name}** in your inventory. Cannot buy more than 100 in total."
            )
            return

        # Update the item counts dictionary with the purchased items
        item_counts[item_name] = item_count + quantity

        # Convert the item counts dictionary back to a string
        new_equipment = ",".join(
            [f"{name}:{count}" for name, count in item_counts.items()]
        )

        # Update the character's money and equipment
        new_money = result[0] - value
        character = (new_money, new_equipment, str(ctx.author.id), character_name)
        self.item.update(character)

        await ctx.send(
            f"Your character **{character_name}** has bought {quantity} unit(s) of {item_name}."
        )

    @commands.command()
    async def view_money(
        self,
        ctx,
        character_name: str = commands.parameter(description="Name of character"),
        player_id: int = commands.parameter(
            description="User ID to fetch character", default=None
        ),
    ):
        """
        Description: View character's money.

        Params:
        !view_money NameOfCharacter UserID

        Example:
        !view_money John
        """

        if player_id is None:
            player_id = str(ctx.author.id)
        else:
            player_id = player_id

        result = self.item.money(player_id, character_name)

        if result is None:
            await ctx.author.send(
                f"You don't have a character named **{character_name}**."
            )
            return

        money = result[0]

        await ctx.author.send(f"Character **{character_name}** has ${money}.")

    @add_item.error
    @remove_item.error
    @view_items.error
    @buy_item.error
    @view_money.error
    async def command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Missing argument. Please check the command syntax and try again."
            )


async def setup(bot):
    await bot.add_cog(Store(bot))
