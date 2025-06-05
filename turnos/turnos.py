from flask import Blueprint, render_template, request, redirect, session, url_for
import json
import os

turnos_bp = Blueprint('turnos', __name__, template_folder="templates")

TURNOS_FILE = "turnos.json"

# Cargar turnos del archivo
def cargar_turnos():
    if not os.path.exists(TURNOS_FILE):
        return []
    with open(TURNOS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

# Guardar turnos en el archivo
def guardar_turnos(turnos):
    try:
        with open(TURNOS_FILE, "w", encoding="utf-8") as f:
            json.dump(turnos, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error al guardar turnos: {e}")

# Validar DNI y mail
def validarDNI(dni):
    return dni.isdigit() and len(dni) == 8

def validarMail(email):
    return "@" in email

# Lista de obras sociales y especialidades
obras_sociales = ["IOMA", "OSDE", "Swiss Medical", "Galeno", "Omint", "Medicus", "Federada Salud", "OSPIP", "PAMI", "OSUTHGRA"]
especialidades = ["Clínica médica", "Pediatría", "Cardiología", "Dermatología", "Ginecología", "Traumatología", "Neurología"]

# Página principal de turnos
@turnos_bp.route("/")
def index():
    if 'usuario' not in session:
        return redirect(url_for('admin.inicio'))

    turnos = cargar_turnos()
    usuario_actual = session.get("usuario")
    rol = session.get("rol")

    if rol != 'admin':
        turnos = [t for t in turnos if t["usuario"] == usuario_actual]
        return render_template("usuario_hud.html", turnos=turnos)
    else:
        return render_template("admin_hud.html", turnos=turnos)

# Crear nuevo turno
@turnos_bp.route("/nuevo", methods=["GET", "POST"])
def nuevo_turno():
    if 'usuario' not in session:
        return redirect(url_for('admin.inicio'))
    
    usuario_actual = session.get("usuario")
    rol = session.get("rol")

    if request.method == "POST":
        nombre = request.form["nombre"].strip().capitalize()
        apellido = request.form["apellido"].strip().capitalize()
        dni = request.form["dni"]
        email = request.form["email"].strip().lower()
        obra_social = request.form["obra_social"]
        fecha = request.form["fecha"]
        hora = request.form["hora"]
        especialidad = request.form["especialidad"]

        if not validarDNI(dni) or not validarMail(email):
            return "Datos inválidos. Volvé a intentarlo."

        turnos = cargar_turnos()

        # ID incremental simple
        nuevo_id = 1
        if turnos:
            nuevo_id = max(t["id"] for t in turnos) + 1

        usuario_actual = session.get("usuario")

        turno = {
            "id": nuevo_id,
            "nombre": nombre,
            "apellido": apellido,
            "dni": dni,
            "email": email,
            "obra_social": obra_social,
            "fecha": fecha,
            "hora": hora,
            "especialidad": especialidad,
            "usuario": usuario_actual
        }

        turnos.append(turno)
        guardar_turnos(turnos)
        return redirect(url_for("turnos.index"))

    datos_usuario = {}
    if rol != 'admin':
        from administrador.admin import usuarios
        datos_usuario = next((u for u in usuarios if u['usuario'] == usuario_actual), {})
    
    if rol == 'admin':
        return render_template(
            "admin_nuevo.html",
            obras_sociales=obras_sociales,
            especialidades=especialidades,
            es_admin=True
        )
    else:
        return render_template(
            "usuario_nuevo.html",
            obras_sociales=obras_sociales,
            especialidades=especialidades,
            datos_usuario=datos_usuario
        )

# Editar turno
@turnos_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if 'usuario' not in session:
        return redirect(url_for('admin.inicio'))

    turnos = cargar_turnos()
    turno = next((t for t in turnos if t["id"] == id), None)
    if not turno:
        return "Turno no encontrado"

    if session.get("rol") != "admin" and turno["usuario"] != session.get("usuario"):
        return "No tenés permiso para editar este turno", 403

    if request.method == "POST":
        turno["nombre"] = request.form["nombre"].strip().capitalize()
        turno["apellido"] = request.form["apellido"].strip().capitalize()
        turno["dni"] = request.form["dni"]
        turno["email"] = request.form["email"].strip().lower()
        turno["obra_social"] = request.form["obra_social"]
        turno["fecha"] = request.form["fecha"]
        turno["hora"] = request.form["hora"]
        turno["especialidad"] = request.form["especialidad"]

        guardar_turnos(turnos)
        return redirect(url_for("turnos.index"))

    return render_template("admin_editar.html", turno=turno, obras_sociales=obras_sociales, especialidades=especialidades)

# Eliminar turno
@turnos_bp.route("/eliminar/<int:id>")
def eliminar(id):
    if 'usuario' not in session:
        return redirect(url_for('admin.inicio'))

    turnos = cargar_turnos()
    turno = next((t for t in turnos if t["id"] == id), None)
    if not turno:
        return "Turno no encontrado"

    if session.get("rol") != "admin" and turno["usuario"] != session.get("usuario"):
        return "No tenés permiso para eliminar este turno", 403

    turnos = [t for t in turnos if t["id"] != id]
    guardar_turnos(turnos)
    return redirect(url_for("turnos.index"))

# Ver historial del usuario
@turnos_bp.route("/mis_turnos")
def mis_turnos():
    if 'usuario' not in session:
        return redirect(url_for('admin.inicio'))

    usuario_actual = session.get("usuario")
    turnos = cargar_turnos()
    mis_turnos = [t for t in turnos if t["usuario"] == usuario_actual]

    return render_template("usuario_hud.html", turnos=mis_turnos)
