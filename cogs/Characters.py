from dotenv import load_dotenv
from discord.ext import commands
import asyncio
import discord
import os
import sqlite3

load_dotenv()

CHARACTER_CHANNEL_ID = int(os.environ["CHARACTER_CHANNEL_ID"])


class Characters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        self.db = sqlite3.connect("swade.db")
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
                money INTEGER,
                UNIQUE(user_id, name)
            )
            """
        )
        self.db.commit()

    async def cog_check(self, ctx):
        return (
            ctx.channel.id == CHARACTER_CHANNEL_ID
            and ctx.guild.me.guild_permissions.manage_messages
        )

    @commands.Cog.listener()
    async def on_command(self, ctx):
        try:
            await asyncio.sleep(30)  # Add a 30-second delay
            await ctx.message.delete()
        except discord.errors.NotFound:
            pass  # The message is already deleted.
        except discord.errors.Forbidden:
            pass  # Bot doesn't have the required permission to delete the message.

    def cog_unload(self):
        self.cursor.close()
        self.db.close()

    @commands.command(aliases=["create"])
    async def createcharacter(
        self,
        ctx,
        name: str = "",
        health: int = 0,
        attributes: str = "",
        skills: str = "",
        equipment: str = "",
        money: int = 0,
    ):
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
        if not isinstance(money, int):
            await ctx.send("Money must be an integer.")
            return

        author_id = str(ctx.author.id)
        cursor = self.db.cursor()

        cursor.execute(
            "SELECT * FROM characters WHERE user_id = ? AND name = ? COLLATE NOCASE",
            (author_id, name),
        )
        existing_character = cursor.fetchone()
        if existing_character:
            await ctx.send(f"A character with the name '{name}' already exists.")
            return

        attributes_string = attributes.replace(",", ", ")
        skills_string = skills.replace(",", ", ")

        cursor.execute(
            "INSERT INTO characters VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                author_id,
                name,
                health,
                attributes_string,
                skills_string,
                equipment,
                money,
            ),
        )
        self.db.commit()

        await ctx.send(f"Character '{name}' created successfully.")

    @commands.command(aliases=["update"])
    async def updatecharacter(self, ctx, name: str, *, kwargs):
        author_id = str(ctx.author.id)
        cursor = self.db.cursor()

        cursor.execute(
            "SELECT * FROM characters WHERE user_id = ? AND name = ? COLLATE NOCASE",
            (author_id, name),
        )
        character = cursor.fetchone()
        if not character:
            await ctx.send(f"Character '{name}' not found.")
            return

        updates = dict(token.split("=") for token in kwargs.split())

        current_attributes = character[3]
        current_skills = character[4]
        current_equipment = character[5]
        current_money = character[6]
        current_health = character[2]

        attributes = updates.get("attributes", current_attributes)
        skills = updates.get("skills", current_skills)
        equipment_updates = updates.get("equipment", "")
        money = int(updates.get("money", current_money))
        health = int(updates.get("health", current_health))

        if attributes != current_attributes:
            existing_attributes = dict(
                attr.split(":") for attr in current_attributes.split(",")
            )
            updated_attributes = dict(attr.split(":") for attr in attributes.split(","))
            merged_attributes = {**existing_attributes, **updated_attributes}
            attributes = ",".join(
                [f"{attr}:{value}" for attr, value in merged_attributes.items()]
            )

        if skills != current_skills:
            existing_skills = dict(
                skill.split(":") for skill in current_skills.split(",")
            )
            updated_skills = dict(skill.split(":") for skill in skills.split(","))
            merged_skills = {**existing_skills, **updated_skills}
            skills = ",".join(
                [f"{skill}:{value}" for skill, value in merged_skills.items()]
            )

        if equipment_updates:
            existing_equipment = {}
            if current_equipment:
                existing_equipment = dict(
                    item.split(":") for item in current_equipment.split(",")
                )

            for item_update in equipment_updates.split(","):
                item_name, item_quantity = item_update.split(":")
                item_quantity = int(item_quantity)

                if item_quantity <= 0:
                    existing_equipment.pop(item_name, None)
                else:
                    existing_equipment[item_name] = str(item_quantity)

            equipment = ",".join(
                [f"{item}:{quantity}" for item, quantity in existing_equipment.items()]
            )
        else:
            equipment = current_equipment

        cursor.execute(
            """
            UPDATE characters
            SET attributes = ?,
                skills = ?,
                equipment = ?,
                money = ?,
                health = ?
            WHERE user_id = ? AND name = ? COLLATE NOCASE
            """,
            (attributes, skills, equipment, money, health, author_id, name),
        )
        self.db.commit()

        await ctx.send(f"Character '{name}' updated successfully.")

    @commands.command(aliases=["dpc"])
    @commands.is_owner()
    async def displayplayercharacter(self, ctx, player: discord.User, name: str):
        cursor = self.db.cursor()

        cursor.execute(
            "SELECT name, health, attributes, skills, equipment, money FROM characters WHERE user_id = ? AND name = ? COLLATE NOCASE",
            (player.id, name),
        )
        character = cursor.fetchone()

        if character is None:
            await ctx.author.send("Player doesn't have any characters yet.")
            return

        name, health, attributes, skills, equipment, money = character

        item_counts = {}
        if equipment:
            items = equipment.split(",")
            for item in items:
                item = item.strip()
                item_name, count = item.split(":")
                item_counts[item_name] = int(count)

        item_lines = []
        for item, count in item_counts.items():
            if count > 1:
                item_lines.append(f"{item} (x{count})")
            else:
                item_lines.append(item)

        embed = discord.Embed(title=f"Character '{name}'", color=discord.Color.green())
        embed.add_field(name="Health", value=str(health), inline=False)
        embed.add_field(
            name="Attributes", value=attributes.replace(",", "\n"), inline=False
        )
        embed.add_field(name="Skills", value=skills.replace(",", "\n"), inline=False)
        embed.add_field(name="Equipment", value="\n".join(item_lines), inline=False)
        embed.add_field(name="Money", value=str(money), inline=False)

        await ctx.send(embed=embed)

    @commands.command(aliases=["display"])
    async def displaycharacter(self, ctx, name: str):
        author_id = str(ctx.author.id)
        cursor = self.db.cursor()

        cursor.execute(
            "SELECT name, health, attributes, skills, equipment, money FROM characters WHERE user_id = ? AND name = ? COLLATE NOCASE",
            (author_id, name),
        )
        character = cursor.fetchone()

        if character is None:
            await ctx.author.send("Character not found.")
            return

        name, health, attributes, skills, equipment, money = character

        item_counts = {}
        if equipment:
            items = equipment.split(",")
            for item in items:
                item = item.strip()
                item_name, count = item.split(":")
                item_counts[item_name] = int(count)

        item_lines = []
        for item, count in item_counts.items():
            if count > 1:
                item_lines.append(f"{item} (x{count})")
            else:
                item_lines.append(item)

        embed = discord.Embed(title=f"Character '{name}'", color=discord.Color.green())
        embed.add_field(name="Health", value=str(health), inline=False)
        embed.add_field(
            name="Attributes", value=attributes.replace(",", "\n"), inline=False
        )
        embed.add_field(name="Skills", value=skills.replace(",", "\n"), inline=False)
        embed.add_field(name="Equipment", value="\n".join(item_lines), inline=False)
        embed.add_field(name="Money", value=str(money), inline=False)

        await ctx.send(embed=embed)

    @commands.command(aliases=["vc"])
    async def viewcharacter(self, ctx, name: str):
        author_id = str(ctx.author.id)
        cursor = self.db.cursor()

        cursor.execute(
            "SELECT name, health, attributes, skills, equipment, money FROM characters WHERE user_id = ? AND name = ? COLLATE NOCASE",
            (author_id, name),
        )
        character = cursor.fetchone()

        if character is None:
            await ctx.author.send("Character not found.")
            return

        name, health, attributes, skills, equipment, money = character

        item_counts = {}
        if equipment:
            items = equipment.split(",")
            for item in items:
                item = item.strip()
                item_name, count = item.split(":")
                item_counts[item_name] = int(count)

        item_lines = []
        for item, count in item_counts.items():
            if count > 1:
                item_lines.append(f"{item} (x{count})")
            else:
                item_lines.append(item)

        embed = discord.Embed(title=f"Character '{name}'", color=discord.Color.green())
        embed.add_field(name="Health", value=str(health), inline=False)
        embed.add_field(
            name="Attributes", value=attributes.replace(",", "\n"), inline=False
        )
        embed.add_field(name="Skills", value=skills.replace(",", "\n"), inline=False)
        embed.add_field(name="Equipment", value="\n".join(item_lines), inline=False)
        embed.add_field(name="Money", value=str(money), inline=False)

        await ctx.author.send(embed=embed)

    @commands.command(aliases=["vpc"])
    @commands.is_owner()
    async def viewplayercharacter(self, ctx, player: discord.User, name: str):
        cursor = self.db.cursor()

        cursor.execute(
            "SELECT name, health, attributes, skills, equipment, money FROM characters WHERE user_id = ? AND name = ? COLLATE NOCASE",
            (player.id, name),
        )
        character = cursor.fetchone()

        if character is None:
            await ctx.author.send("Player doesn't have any characters yet.")
            return

        name, health, attributes, skills, equipment, money = character

        item_counts = {}
        if equipment:
            items = equipment.split(",")
            for item in items:
                item = item.strip()
                item_name, count = item.split(":")
                item_counts[item_name] = int(count)

        item_lines = []
        for item, count in item_counts.items():
            if count > 1:
                item_lines.append(f"{item} (x{count})")
            else:
                item_lines.append(item)

        embed = discord.Embed(title=f"Character '{name}'", color=discord.Color.green())
        embed.add_field(name="Health", value=str(health), inline=False)
        embed.add_field(
            name="Attributes", value=attributes.replace(",", "\n"), inline=False
        )
        embed.add_field(name="Skills", value=skills.replace(",", "\n"), inline=False)
        embed.add_field(name="Equipment", value="\n".join(item_lines), inline=False)
        embed.add_field(name="Money", value=str(money), inline=False)

        await ctx.send(embed=embed)

    @commands.command(aliases=["list"])
    async def viewcharacters(self, ctx):
        author_id = str(ctx.author.id)
        cursor = self.db.cursor()

        cursor.execute(
            "SELECT name, health, attributes, skills, equipment, money FROM characters WHERE user_id = ?",
            (author_id,),
        )
        characters = cursor.fetchall()

        if not characters:
            await ctx.author.send("You don't have any characters yet.")
            return

        for character in characters:
            name, health, attributes, skills, equipment, money = character

            item_counts = {}
            if equipment:
                items = equipment.split(",")
                for item in items:
                    item = item.strip()
                    item_name, count = item.split(":")
                    item_counts[item_name] = int(count)

            item_lines = []
            for item, count in item_counts.items():
                if count > 1:
                    item_lines.append(f"{item} (x{count})")
                else:
                    item_lines.append(item)

            embed = discord.Embed(
                title=f"Character '{name}'", color=discord.Color.green()
            )
            embed.add_field(name="Health", value=str(health), inline=False)
            embed.add_field(
                name="Attributes", value=attributes.replace(",", "\n"), inline=False
            )
            embed.add_field(
                name="Skills", value=skills.replace(",", "\n"), inline=False
            )
            embed.add_field(name="Equipment", value="\n".join(item_lines), inline=False)
            embed.add_field(name="Money", value=str(money), inline=False)

            await ctx.author.send(embed=embed)

    @commands.command(aliases=["vpcs"])
    @commands.is_owner()
    async def viewplayercharacters(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author

        author_id = str(user.id)
        cursor = self.db.cursor()

        cursor.execute(
            "SELECT name, health, attributes, skills, equipment, money FROM characters WHERE user_id = ?",
            (author_id,),
        )
        characters = cursor.fetchall()

        if not characters:
            await ctx.author.send(f"{user.name} doesn't have any characters yet.")
            return

        for character in characters:
            name, health, attributes, skills, equipment, money = character

            item_counts = {}
            if equipment:
                items = equipment.split(",")
                for item in items:
                    item = item.strip()
                    item_name, count = item.split(":")
                    item_counts[item_name] = int(count)

            item_lines = []
            for item, count in item_counts.items():
                if count > 1:
                    item_lines.append(f"{item} (x{count})")
                else:
                    item_lines.append(item)

            embed = discord.Embed(
                title=f"Character '{name}' belonging to {user.name}", color=discord.Color.green()
            )
            embed.add_field(name="Health", value=str(health), inline=False)
            embed.add_field(
                name="Attributes", value=attributes.replace(",", "\n"), inline=False
            )
            embed.add_field(
                name="Skills", value=skills.replace(",", "\n"), inline=False
            )
            embed.add_field(name="Equipment", value="\n".join(item_lines), inline=False)
            embed.add_field(name="Money", value=str(money), inline=False)

            await ctx.author.send(embed=embed)
    
    @commands.command(aliases=["delete"])
    async def deletecharacter(self, ctx, name: str):
        author_id = str(ctx.author.id)
        cursor = self.db.cursor()

        cursor.execute(
            "SELECT * FROM characters WHERE user_id = ? AND name = ? COLLATE NOCASE",
            (author_id, name),
        )
        character = cursor.fetchone()
        if not character:
            await ctx.send(f"Character '{name}' not found.")
            return

        cursor.execute(
            "DELETE FROM characters WHERE user_id = ? AND name = ? COLLATE NOCASE",
            (author_id, name),
        )
        self.db.commit()

        await ctx.send(f"Character '{name}' deleted successfully.")

    @deletecharacter.error
    async def deletecharacter_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a character name.")

    @viewplayercharacter.error
    async def viewplayercharacter_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a player and character name.")

    @viewcharacter.error
    async def viewcharacter_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a character name.")

    @updatecharacter.error
    async def updatecharacter_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Please specify a character name and keyword arguments (health, attributes, skills, or equipment) with updated values."
            )

    @createcharacter.error
    async def createcharacter_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Please specify a character name, health and keyword arguments (attributes, skills, equipment, or money) with initial values."
            )


async def setup(bot):
    await bot.add_cog(Characters(bot))
