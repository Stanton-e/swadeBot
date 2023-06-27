import sqlite3


class Monster:
    def __init__(self):
        self.con = sqlite3.connect("swade.db")
        self.cur = self.con.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute(
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

    def insert(self, monster):
        self.cur.execute(
            """INSERT OR IGNORE INTO monsters (name,health,attributes,skills,equipment,money) VALUES(?,?,?,?,?,?)""",
            monster,
        )
        self.con.commit()

    def read(self, monster_id):
        self.cur.execute("""SELECT * FROM monsters WHERE id = ?""", (monster_id,))
        row = self.cur.fetchone()
        return row

    def read_all(self, monster_id):
        self.cur.execute("""SELECT * FROM monsters WHERE id = ?""", (monster_id,))
        rows = self.cur.fetchall()
        return rows

    def update(self, monster_id, monster):
        self.cur.execute(
            """
            UPDATE monsters
            SET health = ?,
                attributes = ?,
                skills = ?,
                equipment = ?,
                money = ?
            WHERE id = ? AND name = ? COLLATE NOCASE
            """,
            (
                *monster,
                monster_id,
            ),
        )
        self.con.commit()

    def delete(self, monster_id):
        self.cur.execute("""DELETE FROM monsters WHERE id = ?""", (monster_id,))
        self.con.commit()
