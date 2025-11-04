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

# Ejemplo de datos
c.executemany("""
INSERT INTO estudios (dni, numero_estudio, nombre, archivo, fecha)
VALUES (?, ?, ?, ?, ?)
""", [
    ("12345678", "ABC123", "Análisis de Sangre", "/estudios/abc123_sangre.pdf", "2025-10-15"),
    ("12345678", "ABC123", "Radiografía Torácica", "/estudios/abc123_radiografia.pdf", "2025-10-18"),
    ("87654321", "XYZ789", "Electrocardiograma", "/estudios/xyz789_ecg.pdf", "2025-09-10")
])

conn.commit()
conn.close()
