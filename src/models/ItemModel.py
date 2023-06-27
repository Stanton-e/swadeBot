import sqlite3


class Item:
    def __init__(self):
        self.con = sqlite3.connect("swade.db")
        self.cur = self.con.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                name TEXT COLLATE NOCASE,
                category TEXT COLLATE NOCASE,
                price INTEGER,
                UNIQUE(id, name)
            )
            """
        )

    def insert(self, item):
        self.cur.execute(
            """INSERT OR REPLACE INTO items (name,category,price) VALUES(?,?,?)""", item
        )
        self.con.commit()

    def read(self, item_name):
        self.cur.execute("""SELECT * FROM items WHERE name = ?""", (item_name,))
        row = self.cur.fetchone()
        return row

    def read_all(self):
        self.cur.execute("""SELECT * FROM items""")
        rows = self.cur.fetchall()
        return rows

    def delete(self, item_name):
        self.cur.execute("""DELETE FROM items WHERE name = ?""", (item_name,))
        self.con.commit()

    def buy(self, player_id, character_name):
        self.cur.execute(
            """SELECT money, equipment FROM characters WHERE user_id = ? AND name = ? COLLATE NOCASE""",
            (player_id, character_name),
        )
        row = self.cur.fetchone()
        return row

    def update(self, character):
        self.cur.execute(
            """UPDATE characters SET money = ?, equipment = ? WHERE user_id = ? AND name = ? COLLATE NOCASE""",
            character,
        )
        self.con.commit()

    def money(self, player_id, character_name):
        self.cur.execute(
            """SELECT money FROM characters WHERE user_id = ? AND name = ? COLLATE NOCASE""",
            (player_id, character_name),
        )
        row = self.cur.fetchone()
        return row
