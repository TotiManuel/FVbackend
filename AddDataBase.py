import sqlite3

conn = sqlite3.connect("estudios.db")
c = conn.cursor()

c.execute("""
CREATE TABLE estudios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dni TEXT,
    numero_estudio TEXT,
    nombre TEXT,
    archivo TEXT,
    fecha TEXT
)
""")

conn.commit()
conn.close()
