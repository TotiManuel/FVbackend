from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app, origins=["https://fusavim.vercel.app"])  # Permite CORS desde tu frontend

# --- Configuración ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "estudios.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "estudios")  # Carpeta donde se guardan los PDFs

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"pdf"}

# Crear carpeta si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- Función auxiliar ---
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ===============================
# RUTAS PRINCIPALES
# ===============================

@app.route("/")
def home():
    return "API Flask funcionando correctamente 🚀"


# --- Obtener estudios por DNI y número ---
@app.route("/api/estudios", methods=["GET"])
def obtener_estudios():
    dni = request.args.get("dni")
    numero = request.args.get("numero")

    if not dni or not numero:
        return jsonify({"error": "Faltan parámetros: dni y numero"}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nombre, archivo, fecha
        FROM estudios
        WHERE dni = ? AND numero_estudio = ?
    """, (dni, numero))
    resultados = cursor.fetchall()
    conn.close()

    estudios = [
        {"id": r[0], "nombre": r[1], "archivo": r[2], "fecha": r[3]} for r in resultados
    ]
    return jsonify(estudios)

# --- Listar todos los estudios ---
@app.route("/api/estudios/todos", methods=["GET"])
def listar_todos_estudios():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, dni, numero_estudio, nombre, archivo, fecha
        FROM estudios
        ORDER BY fecha DESC
    """)
    resultados = cursor.fetchall()
    conn.close()

    estudios = [
        {
            "id": r[0],
            "dni": r[1],
            "numero_estudio": r[2],
            "nombre": r[3],
            "archivo": r[4],
            "fecha": r[5]
        }
        for r in resultados
    ]
    return jsonify(estudios)


# --- Subir nuevo estudio ---
@app.route("/api/estudios", methods=["POST"])
def subir_estudio():
    dni = request.form.get("dni")
    numero = request.form.get("numero_estudio")
    nombre = request.form.get("nombre")
    fecha = request.form.get("fecha")
    archivo = request.files.get("archivo")

    if not all([dni, numero, nombre, fecha, archivo]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    if not allowed_file(archivo.filename):
        return jsonify({"error": "Solo se permiten archivos PDF"}), 400

    filename = secure_filename(f"{dni}_{numero}_{archivo.filename}")
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    archivo.save(filepath)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO estudios (dni, numero_estudio, nombre, archivo, fecha)
        VALUES (?, ?, ?, ?, ?)
    """, (dni, numero, nombre, f"https://api-fusavim.onrender.com/estudios/{filename}"
, fecha))
    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Estudio subido correctamente"}), 201


# --- Modificar estudio existente ---
@app.route("/api/estudios/<int:id>", methods=["PUT"])
def modificar_estudio(id):
    nombre = request.form.get("nombre")
    fecha = request.form.get("fecha")
    archivo = request.files.get("archivo")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT archivo FROM estudios WHERE id = ?", (id,))
    registro = cursor.fetchone()

    if not registro:
        conn.close()
        return jsonify({"error": "Estudio no encontrado"}), 404

    old_path = registro[0]
    new_path = old_path

    # Si se sube un nuevo archivo, reemplazar el anterior
    if archivo and allowed_file(archivo.filename):
        filename = secure_filename(archivo.filename)
        new_path = f"/estudios/{filename}"
        archivo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        try:
            os.remove(os.path.join(BASE_DIR, old_path.strip("/")))
        except FileNotFoundError:
            pass

    cursor.execute("""
        UPDATE estudios
        SET nombre = ?, fecha = ?, archivo = ?
        WHERE id = ?
    """, (nombre, fecha, new_path, id))
    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Estudio actualizado correctamente"})


# --- Eliminar estudio ---
@app.route("/api/estudios/<int:id>", methods=["DELETE"])
def eliminar_estudio(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT archivo FROM estudios WHERE id = ?", (id,))
    registro = cursor.fetchone()

    if not registro:
        conn.close()
        return jsonify({"error": "Estudio no encontrado"}), 404

    archivo_path = registro[0]
    try:
        os.remove(os.path.join(BASE_DIR, archivo_path.strip("/")))
    except FileNotFoundError:
        pass

    cursor.execute("DELETE FROM estudios WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Estudio eliminado correctamente"})


# --- Servir PDFs ---
@app.route("/estudios/<path:filename>")
def serve_estudio(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ===============================
# EJECUCIÓN LOCAL / RENDER
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
