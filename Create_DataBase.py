import sqlite3 as sq
with sq.connect("Parser.db") as con:
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS logs(
        h TEXT,
        l TEXT,
        u TEXT,
        t TEXT,
        r TEXT,
        s TEXT,
        b TEXT
    , UNIQUE(h, t, r))""")
