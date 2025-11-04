from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app, origins=["https://fusavim.vercel.app"])  # habilita CORS solo para tu frontend

# --- Configuración de la base de datos ---
DB_PATH = os.path.join(os.path.dirname(__file__), "estudios.db")

# --- Rutas ---
@app.route("/")
def home():
    return "API Flask funcionando correctamente 🚀"

@app.route("/api/estudios", methods=["GET"])
def obtener_estudios():
    dni = request.args.get("dni")
    numero = request.args.get("numero")

    if not dni or not numero:
        return jsonify({"error": "Faltan parámetros: dni y numero"}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nombre, archivo, fecha 
        FROM estudios
        WHERE dni = ? AND numero_estudio = ?
    """, (dni, numero))
    resultados = cursor.fetchall()
    conn.close()

    estudios = [
        {"nombre": r[0], "archivo": r[1], "fecha": r[2]} for r in resultados
    ]
    return jsonify(estudios)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
