import sqlite3
from discord.ext import commands


class DatabaseInit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect("swade.db")
        self.cursor = self.db.cursor()

        self.initialize_tables()

    def initialize_tables(self):
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

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS characters (
                user_id INTEGER PRIMARY KEY,
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

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS store(
                item_name TEXT PRIMARY KEY,
                value INTEGER
            );
        """
        )

        self.db.commit()

    def cog_unload(self):
        self.cursor.close()
        self.db.close()


async def setup(bot):
    await bot.add_cog(DatabaseInit(bot))
