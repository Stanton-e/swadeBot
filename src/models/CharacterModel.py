import sqlite3


class Character:
    def __init__(self):
        self.con = sqlite3.connect("swade.db")
        self.cur = self.con.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS characters (
                user_id INTEGER,
                name TEXT COLLATE NOCASE,
                health INTEGER,
                attributes TEXT,
                skills TEXT,
                equipment TEXT,
                money INTEGER
            )
            """
        )

    def insert(self, character):
        self.cur.execute(
            """INSERT OR IGNORE INTO characters VALUES(?,?,?,?,?,?,?)""", character
        )
        self.con.commit()

    def read(self, player_id, character_name):
        self.cur.execute(
            """SELECT * FROM characters WHERE user_id = ? AND name = ? COLLATE NOCASE""",
            (player_id, character_name),
        )
        row = self.cur.fetchone()
        return row

    def read_all(self, player_id):
        self.cur.execute("""SELECT * FROM characters WHERE user_id = ?""", (player_id,))
        rows = self.cur.fetchall()
        return rows

    def update(self, player_id, character_name, character):
        self.cur.execute(
            """
            UPDATE characters
            SET health = ?,
                attributes = ?,
                skills = ?,
                equipment = ?,
                money = ?
            WHERE user_id = ? AND name = ? COLLATE NOCASE
            """,
            (*character, player_id, character_name),
        )
        self.con.commit()

    def delete(self, player_id, character_name):
        self.cur.execute(
            """DELETE FROM characters WHERE user_id = ? AND name = ? COLLATE NOCASE""",
            (player_id, character_name),
        )
        self.con.commit()
