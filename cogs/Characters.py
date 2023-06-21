import discord
from discord.ext import commands
import sqlite3


class Characters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect("characters.db")
        self.cursor = self.db.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS characters (
                user_id INTEGER,
                name TEXT COLLATE NOCASE,
                health INTEGER,
                attributes TEXT,
                skills TEXT,
                equipment TEXT,
                UNIQUE(user_id, name)
            )
            """
        )
        self.db.commit()

    def cog_unload(self):
        self.cursor.close()
        self.db.close()

    @commands.command(aliases=["create"])
    @commands.bot_has_permissions(manage_messages=True)
    async def createcharacter(
        self, ctx, name: str, health: int, attributes: str, skills: str, equipment: str
    ):
        """Create a new character with provided details."""
        # input validation
        if not isinstance(health, int):
            await ctx.send("Health must be an integer.")
            return
        if not isinstance(attributes, str):
            await ctx.send("Attributes must be a string.")
            return
        if not isinstance(skills, str):
            await ctx.send("Skills must be a string.")
            return
        if not isinstance(equipment, str):
            await ctx.send("Equipment must be a string.")
            return

        author_id = str(ctx.author.id)
        cursor = self.db.cursor()

        # Check if the character already exists
        cursor.execute(
            "SELECT * FROM characters WHERE user_id = ? AND name = ? COLLATE NOCASE",
            (author_id, name),
        )
        existing_character = cursor.fetchone()
        if existing_character:
            await ctx.send(f"A character with the name '{name}' already exists.")
            return

        # Insert the character into the database
        cursor.execute(
            "INSERT INTO characters VALUES (?, ?, ?, ?, ?, ?)",
            (author_id, name, health, attributes, skills, equipment),
        )
        self.db.commit()

        await ctx.send(f"Character '{name}' created successfully.")
        await ctx.message.delete()

    @commands.command(aliases=["update"])
    @commands.bot_has_permissions(manage_messages=True)
    async def updatecharacter(self, ctx, name: str, *, kwargs):
        """Update the attributes, skills, or equipment of a character."""
        author_id = str(ctx.author.id)
        cursor = self.db.cursor()

        # Check if the character exists
        cursor.execute(
            "SELECT * FROM characters WHERE user_id = ? AND name = ? COLLATE NOCASE",
            (author_id, name),
        )
        character = cursor.fetchone()
        if not character:
            await ctx.send(f"Character '{name}' not found.")
            return

        # Process the kwargs
        updates = dict(token.split("=") for token in kwargs.split())

        # Update the character's health, attributes, skills, or equipment
        update_values = {}
        for key, value in updates.items():
            if key in ["health", "attributes", "skills", "equipment"]:
                update_values[key] = value

        # Generate the SQL query and values
        query_parts = [f"{key} = ?" for key in update_values.keys()]
        query = f"UPDATE characters SET {', '.join(query_parts)} WHERE user_id = ? AND name = ? COLLATE NOCASE"
        values = list(update_values.values())
        values.extend((author_id, name))

        # Update the character in the database
        cursor.execute(query, tuple(values))
        self.db.commit()

        await ctx.send(f"Character '{name}' updated successfully.")
        await ctx.message.delete()

    @commands.command(aliases=["show"])
    @commands.bot_has_permissions(manage_messages=True)
    async def showcharacters(self, ctx):
        """Show all characters belonging to the user."""
        author_id = str(ctx.author.id)
        cursor = self.db.cursor()

        # Retrieve the user's characters from the database
        cursor.execute(
            "SELECT name, health, attributes, skills, equipment FROM characters WHERE user_id = ?",
            (author_id,),
        )
        characters = cursor.fetchall()

        if not characters:
            await ctx.send("You don't have any characters yet.")
            await ctx.message.delete()
            return

        # Send a separate message for each character's information
        for character in characters:
            name, health, attributes, skills, equipment = character

            embed = discord.Embed(
                title=f"Character '{name}'", color=discord.Color.green()
            )
            embed.add_field(name="Health", value=str(health), inline=False)
            embed.add_field(name="Attributes", value=attributes, inline=False)
            embed.add_field(name="Skills", value=skills, inline=False)
            embed.add_field(name="Equipment", value=equipment, inline=False)

            await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command(aliases=["delete"])
    @commands.bot_has_permissions(manage_messages=True)
    async def deletecharacter(self, ctx, name: str):
        """Delete a character."""
        author_id = str(ctx.author.id)
        cursor = self.db.cursor()

        # Check if the character exists
        cursor.execute(
            "SELECT * FROM characters WHERE user_id = ? AND name = ? COLLATE NOCASE",
            (author_id, name),
        )
        character = cursor.fetchone()
        if not character:
            await ctx.send(f"Character '{name}' not found.")
            return

        # Delete the character in the database
        cursor.execute(
            "DELETE FROM characters WHERE user_id = ? AND name = ? COLLATE NOCASE",
            (author_id, name),
        )
        self.db.commit()

        await ctx.send(f"Character '{name}' deleted successfully.")
        await ctx.message.delete()


async def setup(bot):
    await bot.add_cog(Characters(bot))
