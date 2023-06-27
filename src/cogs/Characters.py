from discord.ext import commands
from dotenv import load_dotenv
from models.CharacterModel import Character
import asyncio
import discord
import os
import sqlite3

load_dotenv()

CHARACTER_CHANNEL_ID = int(os.getenv("CHARACTER_CHANNEL_ID"))


class Characters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        self.character = Character()

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

    @commands.command(aliases=["create"])
    async def create_character(
        self,
        ctx,
        character_name: str = "",
        health: int = 100,
        attributes: str = "",
        skills: str = "",
        equipment: str = "",
        money: int = 0,
    ):
        if not isinstance(character_name, str):
            await ctx.send("Name must be a string.")
            return
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

        player_id = str(ctx.author.id)
        existing_character = self.character.read(player_id, character_name)

        if existing_character:
            await ctx.send(
                f"A character with the name **{character_name}** already exists."
            )
            return

        attributes_string = attributes.replace(",", ", ")
        skills_string = skills.replace(",", ", ")

        character = (
            player_id,
            character_name,
            health,
            attributes_string,
            skills_string,
            equipment,
            money,
        )
        self.character.insert(character)

        await ctx.send(f"Character **{character_name}** created successfully.")

    @commands.command(aliases=["update"])
    async def update_character(self, ctx, character_name: str, *, kwargs):
        player_id = str(ctx.author.id)

        character = self.character.read(player_id, character_name)

        if not character:
            await ctx.send(f"Character **{character_name}** not found.")
            return

        updates = dict(token.split("=") for token in kwargs.split())

        current_health = character[2]
        current_attributes = character[3]
        current_skills = character[4]
        current_equipment = character[5]
        current_money = character[6]

        attributes = updates.get("attributes", current_attributes)
        skills = updates.get("skills", current_skills)
        equipment = updates.get("equipment", current_equipment)
        money = int(updates.get("money", current_money))
        health = int(updates.get("health", current_health))

        if attributes != current_attributes and attributes:
            existing_attributes = dict(
                attr.split(":") for attr in current_attributes.split(",")
            )
            updated_attributes = dict(attr.split(":") for attr in attributes.split(","))
            merged_attributes = {**existing_attributes, **updated_attributes}
            attributes = ",".join(
                [f"{attr}:{value}" for attr, value in merged_attributes.items()]
            )
        elif not current_attributes:
            attributes = updates.get("attributes", "")

        if skills != current_skills and skills:
            existing_skills = dict(
                skill.split(":") for skill in current_skills.split(",")
            )
            updated_skills = dict(skill.split(":") for skill in skills.split(","))
            merged_skills = {**existing_skills, **updated_skills}
            skills = ",".join(
                [f"{skill}:{value}" for skill, value in merged_skills.items()]
            )
        elif not current_skills:
            skills = updates.get("skills", "")

        if equipment:
            existing_equipment = {}
            if current_equipment:
                existing_equipment = dict(
                    item.split(":") for item in current_equipment.split(",")
                )

            for item_update in equipment.split(","):
                item_name, item_quantity = item_update.split(":")
                item_quantity = int(item_quantity)

                if item_quantity <= 0:
                    existing_equipment.pop(item_name, None)
                else:
                    existing_equipment[item_name] = str(item_quantity)

            equipment = ",".join(
                [f"{item}:{quantity}" for item, quantity in existing_equipment.items()]
            )
        elif not current_equipment:
            equipment = updates.get("equipment", "")

        updated_character = (health, attributes, skills, equipment, money)

        self.character.update(player_id, character_name, updated_character)

        await ctx.send(f"Character **{character_name}** updated successfully.")

    @commands.command(aliases=["display"])
    async def display_character(
        self, ctx, character_name: str, player: discord.User = None
    ):
        if player is None:
            player_id = str(ctx.author.id)
        else:
            player_id = player.id

        character = self.character.read(player_id, character_name)

        if character is None:
            await ctx.author.send("Player doesn't have any characters yet.")
            return

        item_counts = {}
        if character[5]:
            items = character[5].split(",")
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
            title=f"Character **{character[1]}**", color=discord.Color.green()
        )
        embed.add_field(name="Health", value=str(character[2]), inline=False)
        embed.add_field(
            name="Attributes", value=character[3].replace(",", "\n"), inline=False
        )
        embed.add_field(
            name="Skills", value=character[4].replace(",", "\n"), inline=False
        )
        embed.add_field(name="Equipment", value="\n".join(item_lines), inline=False)
        embed.add_field(name="Money", value=str(character[6]), inline=False)

        await ctx.send(embed=embed)

    @commands.command(aliases=["view"])
    async def view_character(
        self, ctx, character_name: str, player: discord.User = None
    ):
        if player is None:
            player_id = str(ctx.author.id)
        else:
            player_id = player.id

        character = self.character.read(player_id, character_name)

        if character is None:
            await ctx.author.send("Character not found.")
            return

        item_counts = {}
        if character[5]:
            items = character[5].split(",")
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
            title=f"Character **{character[1]}**", color=discord.Color.green()
        )
        embed.add_field(name="Health", value=str(character[2]), inline=False)
        embed.add_field(
            name="Attributes", value=character[3].replace(",", "\n"), inline=False
        )
        embed.add_field(
            name="Skills", value=character[4].replace(",", "\n"), inline=False
        )
        embed.add_field(name="Equipment", value="\n".join(item_lines), inline=False)
        embed.add_field(name="Money", value=str(character[6]), inline=False)

        await ctx.author.send(embed=embed)

    @commands.command(aliases=["list"])
    async def view_characters(self, ctx, player: discord.User = None):
        if player is None:
            player_id = str(ctx.author.id)
        else:
            player_id = player.id

        characters = self.character.read_all(player_id)

        if not characters:
            await ctx.author.send("You don't have any characters yet.")
            return

        for character in characters:
            item_counts = {}
            if character[5]:
                items = character[5].split(",")
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
                title=f"Character **{character[1]}**", color=discord.Color.green()
            )
            embed.add_field(name="Health", value=str(character[2]), inline=False)
            embed.add_field(
                name="Attributes",
                value=character[3].replace(",", "\n"),
                inline=False,
            )
            embed.add_field(
                name="Skills", value=character[4].replace(",", "\n"), inline=False
            )
            embed.add_field(name="Equipment", value="\n".join(item_lines), inline=False)
            embed.add_field(name="Money", value=str(character[6]), inline=False)

            await ctx.author.send(embed=embed)

    @commands.command(aliases=["delete"])
    async def delete_character(
        self, ctx, character_name: str, player: discord.User = None
    ):
        if player is None:
            player_id = str(ctx.author.id)
        else:
            player_id = player.id

        character = self.character.read(player_id, character_name)

        if not character:
            await ctx.send(f"Character **{character_name}** not found.")
            return

        self.character.delete(player_id, character_name)

        await ctx.send(f"Character **{character_name}** deleted successfully.")

    @delete_character.error
    async def delete_character_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a character name.")

    @view_character.error
    async def view_character_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a character name.")

    @update_character.error
    async def update_character_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Please specify a character name and keyword arguments (health, attributes, skills, or equipment) with updated values."
            )

    @create_character.error
    async def create_character_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Please specify a character name, health and keyword arguments (attributes, skills, equipment, or money) with initial values."
            )


async def setup(bot):
    await bot.add_cog(Characters(bot))
