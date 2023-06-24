from dotenv import load_dotenv
from discord.ext import commands
import asyncio
import discord
import os
import sqlite3

load_dotenv()

TRACKER_CHANNEL_ID = int(os.getenv("TRACKER_CHANNEL_ID"))


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
            ctx.channel.id == TRACKER_CHANNEL_ID
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
    async def createencounter(self, ctx, name: str = ""):
        # Insert the new encounter into the Encounters table
        if not name:
            await ctx.send("Name must not be empty.")
            return

        try:
            with self.db:
                self.cursor.execute(
                    "INSERT INTO encounters (name) VALUES (?)", (name,)
                )
                await ctx.author.send(
                    f"Encounter **{name}** created successfully."
                )
        except sqlite3.Error as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.command(aliases=["de"])
    @commands.is_owner()
    async def deleteencounter(self, ctx, encounter_id: int):
        # Delete encoutner from the Encounters table
        try:
            with self.db:
                self.cursor.execute(
                    "SELECT * FROM encounters WHERE id = ?", (encounter_id,)
                )
                encounter = self.cursor.fetchone()
                if not encounter:
                    await ctx.send(f"Encounter '{encounter_id}' not found.")
                    return

                self.cursor.execute(
                    "DELETE FROM encounters WHERE id = ?", (encounter_id,)
                )
                await ctx.send(
                    f"Encounter **{encounter_id}** deleted successfully."
                )
        except sqlite3.Error as e:
            await ctx.send(f"An error occured: {e}")

    @commands.command(aliases=["fae"])
    @commands.is_owner()
    async def fetchallencounters(self, ctx):
        # Fetches all encounters from the Encounters table
        try:
            with self.db:
                self.cursor.execute("SELECT * FROM encounters")
                encounters = self.cursor.fetchall()
                if not encounters:
                    await ctx.send(f"No encounters have been created yet.")
                    return

                embed = discord.Embed(title="Encounters")
                for encounter in encounters:
                    embed.add_field(
                        name="Encounter Name", value=encounter[1], inline=False
                    )

                await ctx.send(embed=embed)
        except sqlite3.Error as e:
            await ctx.send(f"An error occured: {e}")

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
        if not isinstance(name, str):
            await ctx.send("Name must be a string.")
            return

        try:
            with self.db:
                self.cursor.execute(
                    "INSERT INTO monsters (name, health, attributes, skills, equipment, money) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, health, attributes, skills, equipment, money),
                )
                await ctx.send(f"Monster **{name}** created successfully.")
        except sqlite3.Error as e:
            await ctx.send(f"An error occured: {e}")

    @commands.command(aliases=["dm"])
    @commands.is_owner()
    async def deletemonster(self, ctx, monster_id: int):
        # Delete monster from the Monsters table
        try:
            with self.db:
                self.cursor.execute(
                    "SELECT * FROM monsters WHERE id = ?", (monster_id,)
                )
                monster = self.cursor.fetchone()
                if not monster:
                    await ctx.send(f"Monster '{monster_id}' not found.")
                    return

                self.cursor.execute(
                    "DELETE FROM monsters WHERE id = ?", (monster_id,)
                )
                await ctx.send(
                    f"Monster **{monster_id}** deleted successfully."
                )
        except sqlite3.Error as e:
            await ctx.send(f"An error occured: {e}")

    @commands.command(aliases=["ac2e"])
    @commands.is_owner()
    async def addcharactertoencounter(
        self, ctx, encounter_id: int, player: discord.User, name: str
    ):
        # Insert a row into the Encounter_Characters table
        if not isinstance(encounter_id, int):
            await ctx.send("Encounter_ID must be an int.")
            return
        if not isinstance(name, str):
            await ctx.send("Name must be a string.")
            return

        try:
            with self.db:
                self.cursor.execute(
                    "INSERT INTO encounter_characters (encounter_ID, player_ID, character_name) VALUES (?, ?, ?)",
                    (encounter_id, player.id, name),
                )

                embed = discord.Embed(
                    title="Character Added to Encounter",
                    description=f"Character **{name}** added to encounter successfully",
                    color=discord.Color.yellow(),
                )

                await ctx.send(embed=embed)
        except sqlite3.Error as e:
            await ctx.send(f"An error occured: {e}")

    @commands.command(aliases=["am2e"])
    @commands.is_owner()
    async def addmonstertoencounter(
        self, ctx, encounter_id: int, monster_id: int
    ):
        # Insert a row into the Encounter_Monsters table
        try:
            with self.db:
                self.cursor.execute(
                    "SELECT name FROM monsters WHERE id = ?", (monster_id,)
                )
                monster_name = self.cursor.fetchone()[0]

                self.cursor.execute(
                    "INSERT INTO encounter_monsters (encounter_id, monster_id) VALUES (?, ?)",
                    (encounter_id, monster_id),
                )

                embed = discord.Embed(
                    title="Monster Added to Encounter",
                    description=f"Monster **{monster_name}** added to encounter successfully",
                    color=discord.Color.yellow(),
                )

                await ctx.send(embed=embed)
        except sqlite3.Error as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.command(aliases=["ge"])
    @commands.is_owner()
    async def getencounter(self, ctx, encounter_id: int):
        # Get the encounter from the Encounters table
        if not isinstance(encounter_id, int):
            await ctx.send("Encounter_ID must be an int.")
            return

        try:
            with self.db:
                self.cursor.execute(
                    "SELECT * FROM encounters WHERE id = ?", (encounter_id,)
                )
                encounter = self.cursor.fetchone()
                await ctx.send(f"Encounter: **{encounter[1]}**")
        except sqlite3.Error as e:
            await ctx.send(f"An error occured: {e}")

    @commands.command(aliases=["gcie"])
    @commands.is_owner()
    async def getcharactersinencounter(self, ctx, encounter_id: int):
        # Get all characters in an encounter
        if not isinstance(encounter_id, int):
            await ctx.send("Encounter_ID must be an int.")
            return

        try:
            with self.db:
                self.cursor.execute(
                    "SELECT name FROM encounters WHERE id = ?", (encounter_id,)
                )
                encounter_name = self.cursor.fetchone()[0]

                self.cursor.execute(
                    "SELECT * FROM characters WHERE user_id IN (SELECT player_ID FROM encounter_characters WHERE encounter_id = ?)",
                    (encounter_id,),
                )
                characters = self.cursor.fetchall()

                embed = discord.Embed(
                    title="Characters in Encounter",
                    description=f"Encounter Name: **{encounter_name}**",
                    color=0x00FF00,
                )
                for character in characters:
                    embed.add_field(
                        name="Character Name", value=character[1], inline=False
                    )
                    embed.add_field(
                        name="Health", value=character[2], inline=True
                    )

                await ctx.send(embed=embed)
        except sqlite3.Error as e:
            await ctx.send(f"An error occured: {e}")

    @commands.command(aliases=["gmie"])
    @commands.is_owner()
    async def getmonstersinencounter(self, ctx, encounter_id: int):
        # Get all monsters in an encounter
        if not isinstance(encounter_id, int):
            await ctx.send("Encounter_ID must be an int.")
            return

        try:
            with self.db:
                self.cursor.execute(
                    "SELECT name FROM encounters WHERE id = ?", (encounter_id,)
                )
                encounter_name = self.cursor.fetchone()[0]

                self.cursor.execute(
                    "SELECT * FROM monsters WHERE id IN (SELECT monster_id FROM encounter_monsters WHERE encounter_id = ?)",
                    (encounter_id,),
                )
                monsters = self.cursor.fetchall()

                embed = discord.Embed(
                    title="Monsters in Encounter",
                    description=f"Encounter Name: **{encounter_name}**",
                    color=0xFF0000,
                )
                for monster in monsters:
                    embed.add_field(
                        name="Monster Name", value=monster[1], inline=False
                    )
                    embed.add_field(
                        name="Health", value=monster[2], inline=True
                    )

                await ctx.send(embed=embed)
        except sqlite3.Error as e:
            await ctx.send(f"An error occured: {e}")

    @commands.command(aliases=["rcfe"])
    @commands.is_owner()
    async def removecharacterfromencounter(
        self, ctx, encounter_id: int, player: discord.User, name: str
    ):
        # Remove a character from an encounter
        if not isinstance(encounter_id, int):
            await ctx.send("Encounter_ID must be an int.")
            return

        try:
            with self.db:
                self.cursor.execute(
                    "DELETE FROM encounter_characters WHERE encounter_id = ? AND player_id = ? AND character_name = ?",
                    (encounter_id, player.id, name),
                )

                embed = discord.Embed(
                    title="Character Removed from Encounter",
                    description=f"Character **{name}** removed from encounter successfully",
                    color=discord.Color.yellow(),
                )

                await ctx.send(embed=embed)
        except sqlite3.Error as e:
            await ctx.send(f"An error occured: {e}")

    @commands.command(aliases=["rmfe"])
    @commands.is_owner()
    async def removemonsterfromencounter(
        self, ctx, encounter_id: int, monster_id: int
    ):
        # Remove a monster from an encounter
        if not isinstance(encounter_id, int):
            await ctx.send("Encounter ID must be an int.")
            return
        if not isinstance(monster_id, int):
            await ctx.send("Monster ID must be an int.")
            return

        try:
            with self.db:
                self.cursor.execute(
                    "SELECT name FROM monsters WHERE id = ?", (monster_id,)
                )
                monster_name = self.cursor.fetchone()[0]

                self.cursor.execute(
                    "DELETE FROM encounter_monsters WHERE encounter_id = ? AND monster_id = ?",
                    (encounter_id, monster_id),
                )

                embed = discord.Embed(
                    title="Monster Removed from Encounter",
                    description=f"Monster **{monster_name}** removed from encounter successfully",
                    color=discord.Color.yellow(),
                )

                await ctx.send(embed=embed)
        except sqlite3.Error as e:
            await ctx.send(f"An error occured: {e}")

    @commands.command(aliases=["uchp"])
    @commands.is_owner()
    async def updatecharacterhp(
        self, ctx, player: discord.User, name: str, new_hp: int
    ):
        # Update a character's HP
        try:
            with self.db:
                self.cursor.execute(
                    "UPDATE characters SET health = ? WHERE user_id = ? AND name = ?",
                    (new_hp, player.id, name),
                )
                await ctx.send(
                    f"Character **{name}** now has **{new_hp}** for health."
                )
        except sqlite3.Error as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.command(aliases=["umhp"])
    @commands.is_owner()
    async def updatemonsterhp(self, ctx, monster_id: int, new_hp: int):
        # Update a monster's HP
        if not isinstance(monster_id, int):
            await ctx.send("Encounter ID must be an int.")
            return
        if not isinstance(new_hp, int):
            await ctx.send("New HP must be an int.")
            return

        try:
            with self.db:
                self.cursor.execute(
                    "UPDATE monsters SET health = ? WHERE id = ?",
                    (new_hp, monster_id),
                )
                await ctx.send(
                    f"Monster **{monster_id}** now has **{new_hp}** for health."
                )
        except sqlite3.Error as e:
            await ctx.send(f"An error occurred: {e}")
