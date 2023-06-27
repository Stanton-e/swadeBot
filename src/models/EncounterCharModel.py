import sqlite3


class EncounterChar:
    def __init__(self):
        self.con = sqlite3.connect("swade.db")
        self.cur = self.con.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute(
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

    def insert(self, encounter_character):
        self.cur.execute(
            """INSERT OR IGNORE INTO encounter_characters VALUES(?,?,?)""",
            encounter_character,
        )
        self.con.commit()

    def read(self, encounter_id):
        self.cur.execute("SELECT name FROM encounters WHERE id = ?", (encounter_id,))
        row = self.cur.fetchone()
        encounter_name = row[0] if row else None

        self.cur.execute(
            """SELECT * FROM characters WHERE user_id IN (SELECT player_id FROM encounter_characters WHERE encounter_id = ?)""",
            (encounter_id,),
        )
        rows = self.cur.fetchall()
        return encounter_name, rows

    def read_all(self):
        self.cur.execute("""SELECT * FROM encounter_characters""")
        rows = self.cur.fetchall()
        return rows

    def delete(self, encounter_character):
        self.cur.execute(
            """DELETE FROM encounter_characters WHERE encounter_id = ? AND player_id = ? AND character_name = ?""",
            encounter_character,
        )
        self.con.commit()
