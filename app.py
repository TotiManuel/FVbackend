from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return "API Flask funcionando correctamente 🚀"

@app.route("/api/estudios", methods=["GET"])
def obtener_estudios():
    dni = request.args.get("dni")
    numero = request.args.get("numero")

    conn = sqlite3.connect("estudios.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nombre, archivo, fecha FROM estudios
        WHERE dni = ? AND numero_estudio = ?
    """, (dni, numero))
    resultados = cursor.fetchall()
    conn.close()

    estudios = [
        {"nombre": r[0], "archivo": r[1], "fecha": r[2]} for r in resultados
    ]
    return jsonify(estudios)

if __name__ == "__main__":
    from flask_cors import CORS
    CORS(app)  # Para permitir que tu frontend en Vercel se conecte
    app.run(host="0.0.0.0", port=5000)
