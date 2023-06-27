import sqlite3


class EncounterMon:
    def __init__(self):
        self.con = sqlite3.connect("swade.db")
        self.cur = self.con.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS encounter_monsters (
                encounter_id INTEGER,
                monster_id INTEGER,
                FOREIGN KEY(encounter_id) REFERENCES encounters(id)
                FOREIGN KEY(monster_id) REFERENCES monsters(id)
            )
            """
        )

    def insert(self, encounter_monster):
        self.cur.execute(
            """INSERT OR IGNORE INTO encounter_monsters VALUES(?,?)""",
            encounter_monster,
        )
        self.con.commit()

    def read(self, encounter_id):
        self.cur.execute("SELECT name FROM encounters WHERE id = ?", (encounter_id,))
        row = self.cur.fetchone()
        encounter_name = row[0] if row else None

        self.cur.execute(
            """SELECT * FROM monsters WHERE id IN (SELECT monster_id FROM encounter_monsters WHERE encounter_id = ?)""",
            (encounter_id,),
        )
        rows = self.cur.fetchall()
        return encounter_name, rows

    def read_all(self):
        self.cur.execute("""SELECT * FROM encounter_monsters""")
        rows = self.cur.fetchall()
        return rows

    def delete(self, encounter_monster):
        self.cur.execute(
            """DELETE FROM encounter_monsters WHERE encounter_id = ? AND monster_id = ?""",
            encounter_monster,
        )
        self.con.commit()
