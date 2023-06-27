import sqlite3


class Encounter:
    def __init__(self):
        self.con = sqlite3.connect("swade.db")
        self.cur = self.con.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS encounters (
                id INTEGER PRIMARY KEY,
                name TEXT COLLATE NOCASE,
                UNIQUE(id)
            )
            """
        )

    def insert(self, name):
        self.cur.execute("""INSERT INTO encounters (name) VALUES(?)""", (name,))
        self.con.commit()

    def read(self, encounter_id):
        self.cur.execute("""SELECT * FROM encounters WHERE id = ?""", (encounter_id,))
        row = self.cur.fetchone()
        return row

    def read_all(self):
        self.cur.execute("""SELECT * FROM encounters""")
        rows = self.cur.fetchall()
        return rows

    def delete(self, encounter_id):
        self.cur.execute(
            """DELETE FROM encounters WHERE id = ?""",
            (encounter_id,),
        )
        self.con.commit()
