from dotenv import load_dotenv
from discord.ext import commands
import asyncio
import discord
import os
import sqlite3

load_dotenv()

MAIN_CHANNEL_ID = int(os.getenv("MAIN_CHANNEL_ID"))


class Encounters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.encounters = {}
        self.db = sqlite3.connect("swade.db")
        self.cursor = self.db.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS monsters (
                id INTEGER PRIMARY KEY,
                name TEXT COLLATE NOCASE,
                health INTEGER,
                attributes TEXT,
                skills TEXT,
                equipment TEXT,
                money INTEGER,
                UNIQUE(id)
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS encounters (
                id INTEGER PRIMARY KEY,
                name TEXT COLLATE NOCASE,
                UNIQUE(id)
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS encounter_characters (
                encounter_id INTEGER,
                player_id INTEGER,
                character_name TEXT COLLATE NOCASE,
                FOREIGN KEY(encounter_id) REFERENCES encounters(id),
                FOREIGN KEY(player_id) REFERENCES characters(user_id)
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS encounter_monsters (
                encounter_id INTEGER,
                monster_id INTEGER,
                FOREIGN KEY(encounter_id) REFERENCES encounters(id),
                FOREIGN KEY(monster_id) REFERENCES monsters(id)
            )
            """
        )
        self.db.commit()

    async def cog_check(self, ctx):
        return (
            ctx.channel.id == MAIN_CHANNEL_ID
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

    @commands.command(aliases=["ce"])
    @commands.is_owner()
    async def createencounter(
        self,
        ctx,
        name: str = "",
    ):
        # Insert the new encounter into the Encounters table
        cursor = self.db.cursor()
        if not isinstance(name, str):
            await ctx.send("Name must be a string.")
            return

        cursor.execute("INSERT INTO encounters (name) VALUES (?)", (name,))
        self.db.commit()

        await ctx.send(f"Encounter '{name}' created successfully.")


    @commands.command(aliases=["cm"])
    @commands.is_owner()
    async def createmonster(
        self,
        ctx,
        name: str = "",
        health: int = 100,
        attributes: str = "",
        skills: str = "",
        equipment: str = "",
        money: int = 0,
    ):
        # Insert the new monster into the Monsters table
        cursor = self.db.cursor()
        if not isinstance(name, str):
            await ctx.send("Name must be a string.")
            return

        cursor.execute("INSERT INTO monsters (name, health, attributes, skills, equipment, money) VALUES (?, ?, ?, ?, ?, ?)", (name, health, attributes, skills, equipment, money,))
        self.db.commit()

        await ctx.send(f"Monster '{name}' created successfully.")

    @commands.command(aliases=["ac2e"])
    @commands.is_owner()
    async def addcharactertoencounter(
        self,
        ctx,
        encounter_id: int,
        player: discord.User,
        name: str,
    ):
        # Insert a row into the Encounter_Characters table
        cursor = self.db.cursor()
        if not isinstance(encounter_id, int):
            await ctx.send("Encounter_ID must be an int.")
            return
        if not isinstance(name, str):
            await ctx.send("Name must be a string.")
            return

        cursor.execute(
            "INSERT INTO encounter_characters (encounter_ID, player_ID, character_name) VALUES (?, ?, ?)",
            (
                encounter_id,
                player.id,
                name,
            ),
        )
        self.db.commit()

        await ctx.send(f"Character '{name}' added to encounter successfully.")

    @commands.command(aliases=["am2e"])
    @commands.is_owner()
    async def addmonstertoencounter(
        self,
        ctx,
        encounter_id: int,
        monster_id: int,
    ):
        # Insert a row into the Encounter_Monsters table
        cursor = self.db.cursor()
        if not isinstance(encounter_id, int):
            await ctx.send("Encounter_ID must be an int.")
            return
        if not isinstance(monster_id, int):
            await ctx.send("Monster_ID must be an int.")
            return

        cursor.execute(
            "INSERT INTO encounter_monsters (encounter_id, monster_id) VALUES (?, ?)",
            (encounter_id, monster_id),
        )
        self.db.commit()

        await ctx.send(f"Monster '{monster_id}' added to encounter successfully.")

    @commands.command(aliases=["ge"])
    @commands.is_owner()
    async def getencounter(
        self,
        ctx,
        encounter_id: int,
    ):
        # Get the encounter from the Encounters table
        cursor = self.db.cursor()
        if not isinstance(encounter_id, int):
            await ctx.send("Encounter_ID must be an int.")
            return

        cursor.execute("SELECT * FROM encounters WHERE id = ?", (encounter_id,))
        encounter = cursor.fetchone()
        await ctx.send(f"Encounter: '{encounter}'")
        return encounter

    @commands.command(aliases=["gcie"])
    @commands.is_owner()
    async def getcharactersinencounter(
        self,
        ctx,
        encounter_id: int,
    ):
        # Get all characters in an encounter
        cursor = self.db.cursor()
        if not isinstance(encounter_id, int):
            await ctx.send("Encounter_ID must be an int.")
            return

        cursor.execute(
            "SELECT * FROM characters WHERE user_id IN (SELECT player_ID FROM encounter_characters WHERE encounter_id = ?)",
            (encounter_id,),
        )
        characters = cursor.fetchall()
        await ctx.send(f"Characters: '{characters}'")
        return characters

    @commands.command(aliases=["gmie"])
    @commands.is_owner()
    async def getmonstersinencounter(
        self,
        ctx,
        encounter_id: int,
    ):
        # Get all monsters in an encounter
        cursor = self.db.cursor()
        if not isinstance(encounter_id, int):
            await ctx.send("Encounter_ID must be an int.")
            return

        cursor.execute(
            "SELECT * FROM monsters WHERE id IN (SELECT monster_id FROM encounter_monsters WHERE encounter_id = ?)",
            (encounter_id,),
        )
        monsters = cursor.fetchall()
        await ctx.send(f"Monsters: '{monsters}'")
        return monsters

    @commands.command(aliases=["rcfe"])
    @commands.is_owner()
    async def removecharacterfromencounter(
        self,
        ctx,
        encounter_id: int,
        player: discord.User,
        name: str,
    ):
        # Remove a character from an encounter
        cursor = self.db.cursor()
        if not isinstance(encounter_id, int):
            await ctx.send("Encounter_ID must be an int.")
            return

        cursor.execute(
            "DELETE FROM encounter_characters WHERE encounter_id = ? AND player_id = ? AND character_name = ?",
            (encounter_id, player.id, name),
        )
        self.db.commit()

        await ctx.send(f"Character '{name}' removed from encounter successfully.")

    @commands.command(aliases=["rmfe"])
    @commands.is_owner()
    async def removemonsterfromencounter(
        self,
        ctx,
        encounter_id: int,
        monster_id: int,
    ):
        # Remove a monster from an encounter
        cursor = self.db.cursor()
        if not isinstance(encounter_id, int):
            await ctx.send("Encounter_ID must be an int.")
            return
        if not isinstance(monster_id, int):
            await ctx.send("Monster_ID must be an int.")
            return

        cursor.execute(
            "DELETE FROM encounter_monsters WHERE encounter_id = ? AND monster_id = ?",
            (encounter_id, monster_id),
        )
        self.db.commit()

        await ctx.send(f"Monster '{monster_id}' removed from encounter successfully.")

    @commands.command(aliases=["uchp"])
    @commands.is_owner()
    async def updatecharacterhp(
        self,
        ctx,
        player: discord.User,
        name: str,
        new_hp: int,
    ):
        # Update a character's HP
        cursor = self.db.cursor()
        if not isinstance(new_hp, int):
            await ctx.send("New_Hp must be an int.")
            return

        cursor.execute(
            "UPDATE characters SET health = ? WHERE user_id = ? AND name = ?",
            (new_hp, player.id, name),
        )
        self.db.commit()

        await ctx.send(f"Character '{name}' now has '{new_hp}' for health.")

    @commands.command(aliases=["umhp"])
    @commands.is_owner()
    async def updatemonsterhp(
        self,
        ctx,
        monster_id: int,
        new_hp: int,
    ):
        # Update a monster's HP
        cursor = self.db.cursor()
        if not isinstance(monster_id, int):
            await ctx.send("Monster_ID must be an int.")
            return
        if not isinstance(new_hp, int):
            await ctx.send("New_Hp must be an int.")
            return

        cursor.execute(
            "UPDATE monsters SET health = ? WHERE id = ?", (new_hp, monster_id)
        )
        self.db.commit()

        await ctx.send(f"Monster '{monster_id}' now has '{new_hp}' for health.")
