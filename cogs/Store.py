from dotenv import load_dotenv
from discord.ext import commands
import os
import sqlite3

load_dotenv()

MARKET_CHANNEL_ID = int(os.environ["MARKET_CHANNEL_ID"])


class Store(commands.Cog):
    def cog_check(self, ctx):
        return ctx.message.channel.id == MARKET_CHANNEL_ID

    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("characters.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS store(
                item_name TEXT PRIMARY KEY,
                value INTEGER
            );
        """
        )

    def cog_unload(self):
        self.cursor.close()
        self.conn.close()

    @commands.command()
    @commands.is_owner()
    async def add_item(self, ctx, item_name, value: int):
        if not isinstance(value, int) or value <= 0:
            await ctx.send("Value must be a positive integer.")
            return

        self.cursor.execute("INSERT INTO store VALUES (?, ?)", (item_name, value))
        self.conn.commit()

        await ctx.send(f"Added {item_name} to the store with a value of {value}.")

    @commands.command()
    @commands.is_owner()
    async def remove_item(self, ctx, item_name):
        self.cursor.execute("DELETE FROM store WHERE item_name = ?", (item_name,))
        self.conn.commit()

        await ctx.send(f"Removed {item_name} from the store.")

    @commands.command()
    async def view_items(self, ctx):
        self.cursor.execute("SELECT * FROM store")
        items = self.cursor.fetchall()

        if not items:
            await ctx.send("The store is currently empty.")
            return

        message = "Items available in the store:\n"
        for item_name, value in items:
            message += f"{item_name}: {value}\n"

        await ctx.send(message)

    @commands.command()
    async def buy_item(self, ctx, character_name, item_name, quantity: int = 1):
        self.cursor.execute("SELECT value FROM store WHERE item_name = ?", (item_name,))
        result = self.cursor.fetchone()

        if result is None:
            await ctx.send(f"The item {item_name} does not exist in the store.")
            return

        value = result[0] * quantity

        self.cursor.execute(
            """
            SELECT money, equipment FROM characters
            WHERE user_id = ? AND name = ? COLLATE NOCASE
        """,
            (str(ctx.author.id), character_name),
        )
        result = self.cursor.fetchone()

        if result is None:
            await ctx.send(f"You don't have a character named {character_name}.")
            return

        char_money, equipment = result
        if char_money < value:
            await ctx.send(
                f"Your character {character_name} does not have enough money to buy this item."
            )
            return

        # If the character has enough money, subtract the value from the character's money and add the item to the character's equipment
        new_equipment = (
            equipment + "," + item_name * quantity
            if equipment
            else item_name * quantity
        )

        # Update the character's money and equipment
        new_money = char_money - value
        self.cursor.execute(
            """
            UPDATE characters
            SET money = ?, equipment = ?
            WHERE user_id = ? AND name = ? COLLATE NOCASE
        """,
            (new_money, new_equipment, str(ctx.author.id), character_name),
        )

        self.conn.commit()

        await ctx.send(
            f"Your character {character_name} has bought {quantity} unit(s) of {item_name}."
        )

    @add_item.error
    @remove_item.error
    @view_items.error
    @buy_item.error
    async def command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Missing argument. Please check the command syntax and try again."
            )


async def setup(bot):
    await bot.add_cog(Store(bot))
