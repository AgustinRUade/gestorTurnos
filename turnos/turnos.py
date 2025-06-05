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

# Este apartado te dirige a la pagina inicial del admin/usuario desde el login
@turnos_bp.route("/")
def index():
    if 'usuario' not in session:
        return redirect(url_for('admin.inicio'))

    # Se encarga de buscar los turnos de JSON, busca el usuario actual y lo guarda, y asigna el rol
    turnos = cargar_turnos()
    usuario_actual = session.get("usuario")
    rol = session.get("rol")

    # Si el usuario no es un admin solo se muestran sus turnos propios
    if rol != 'admin':
        turnos = [t for t in turnos if t["usuario"] == usuario_actual]
        return render_template("usuario_hud.html", turnos=turnos)
    #En caso de ser admin podra ver todos los turnos disponibles
    else:
        return render_template("admin_hud.html", turnos=turnos)

# Apartado que permite la creacion de un nuevo turno
@turnos_bp.route("/nuevo", methods=["GET", "POST"])
def nuevo_turno():
    if 'usuario' not in session:
        return redirect(url_for('admin.inicio'))
    
    #busca el usuario actual y lo guarda, y asigna el rol
    usuario_actual = session.get("usuario")
    rol = session.get("rol")

    #Al enviar el formulario se obtienen los datos y los asignamos a variables
    if request.method == "POST":
        nombre = request.form["nombre"].strip().capitalize()
        apellido = request.form["apellido"].strip().capitalize()
        dni = request.form["dni"]
        email = request.form["email"].strip().lower()
        obra_social = request.form["obra_social"]
        fecha = request.form["fecha"]
        hora = request.form["hora"]
        especialidad = request.form["especialidad"]

        #Valida el dni y el mail
        if not validarDNI(dni) or not validarMail(email):
            return "Datos inválidos. Volvé a intentarlo."

        #Guardamos en una variable los turnos existentes que estaban en el JSON
        turnos = cargar_turnos()

        # Incrementa el DNI en uno (esto se va a cambiar mas adelante)
        nuevo_id = 1
        if turnos:
            nuevo_id = max(t["id"] for t in turnos) + 1

        #chequea quien esta usando el programa
        usuario_actual = session.get("usuario")

        #Guardamos los datos en una biblioteca para mandarlo al JSON
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
        
        #Enviamos a JSON
        turnos.append(turno)
        guardar_turnos(turnos)
        
        #Volvemos al Hud
        return redirect(url_for("turnos.index"))

    #Si el usuario no es admin lo guardamos para que lo vea como sus turnos
    datos_usuario = {}
    if rol != 'admin':
        from administrador.admin import usuarios
        datos_usuario = next((u for u in usuarios if u['usuario'] == usuario_actual), {})
    
    #Si es admin mostramos el html para crear turno como admin
    if rol == 'admin':
        return render_template(
            "admin_nuevo.html",
            obras_sociales=obras_sociales,
            especialidades=especialidades,
            es_admin=True
        )
    #Si es usuario mostramos el html para crear turno como usuario
    else:
        return render_template(
            "usuario_nuevo.html",
            obras_sociales=obras_sociales,
            especialidades=especialidades,
            datos_usuario=datos_usuario
        )

# Este apartado sirve para editar los turnos existentes
@turnos_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if 'usuario' not in session:
        return redirect(url_for('admin.inicio'))

    #Cargamos los turnos ya creados y chequeamos el id del seleccionado
    turnos = cargar_turnos()
    turno = next((t for t in turnos if t["id"] == id), None)
    if not turno:
        return "Turno no encontrado"

    #Esto hace que cualquiera que no este registrado en la pagina no pueda ingresar manualmente
    if session.get("rol") != "admin" and turno["usuario"] != session.get("usuario"):
        return "No tenés permiso para editar este turno", 403

    #Reescribimos los datos anteriores
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

        #Volvemos al hud segun seamos admin o usuario
        return redirect(url_for("turnos.index"))

    #Cargamos el html de admin_editar
    return render_template("admin_editar.html", turno=turno, obras_sociales=obras_sociales, especialidades=especialidades)

# Este es para eliminar turnos
@turnos_bp.route("/eliminar/<int:id>")
def eliminar(id):
    if 'usuario' not in session:
        return redirect(url_for('admin.inicio'))

    #Cargamos los turnos y seleccionamos por id
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
# @turnos_bp.route("/mis_turnos")
# def mis_turnos():
#     if 'usuario' not in session:
#         return redirect(url_for('admin.inicio'))

#     usuario_actual = session.get("usuario")
#     turnos = cargar_turnos()
#     mis_turnos = [t for t in turnos if t["usuario"] == usuario_actual]

#     return render_template("usuario_hud.html", turnos=mis_turnos)
