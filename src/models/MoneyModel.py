import sqlite3


class Money:
    def __init__(self):
        self.con = sqlite3.connect("swade.db")
        self.cur = self.con.cursor()

    def add(self, player_id, character_name, amount):
        self.cur.execute(
            """UPDATE characters SET money = money + ? WHERE user_id = ? AND name= ? COLLATE NOCASE""",
            (amount, player_id, character_name),
        )
        self.con.commit()

    def subtract(self, player_id, character_name, amount):
        self.cur.execute(
            """UPDATE characters SET money = money - ? WHERE user_id = ? AND name= ? COLLATE NOCASE""",
            (amount, player_id, character_name),
        )
        self.con.commit()

    def read(self, player_id, character_name):
        self.cur.execute(
            """SELECT money FROM characters WHERE user_id = ? AND name = ? COLLATE NOCASE""",
            (player_id, character_name),
        )
        row = self.cur.fetchone()
        return row
