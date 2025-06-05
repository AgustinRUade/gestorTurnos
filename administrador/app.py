#Aca generamos la matriz de turnos (de momento vacia)
#Creamos el CRUD para crear, ver, editar y borrar los turnos
from flask import Blueprint, render_template, request, redirect, session, url_for
import json
import os

pacientes_bp = Blueprint('clientes', __name__, url_prefix="/pacientes", template_folder="templates") 

PACIENTES_FILE = "pacientes.json"

# Función para cargar la lista de pacientes desde el archivo JSON.
# Si el archivo no existe o está vacío, devuelve una lista vacía.
def cargar_pacientes():
    if not os.path.exists(PACIENTES_FILE):
        return []
    with open(PACIENTES_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # Si el archivo está corrupto o vacío, retorna una lista vacía
            return []

# Función para guardar la lista de pacientes en el archivo JSON.
# Sobrescribe el archivo con la nueva lista de pacientes.
def guardar_pacientes(pacientes):
    try:
        with open(PACIENTES_FILE, "w", encoding="utf-8") as f:
            json.dump(pacientes, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error al guardar pacientes: {e}") #Imprime que hubo un error al guardar los pacientes


#Lista de obras sociales
#Esta lista es para que el usuario pueda elegir la obra social
obras_sociales = [
    "IOMA",
    "OSDE",
    "Swiss Medical",
    "Galeno",
    "Omint",
    "Medicus",
    "Federada Salud",
    "OSPIP",
    "PAMI",
    "OSUTHGRA"
]

#Hacemos que el dni sea de 8 digitos y que se asegure son sumeros
def validarDNI(dni):
    return dni.isdigit() and len(dni) == 8

#En este vemos que tenga el @
def validarMail(email):
    return "@" in email

#Ruta princiapl
@pacientes_bp.route("/")
def index():
    if 'usuario' not in session:
        return redirect(url_for('admin.inicio')) # Esto hace que alguien no logueado pueda ingresar
    
    # Cargamos los datos del .json
    pacientes = cargar_pacientes()
    usuario_actual = session.get("usuario")
    rol = session.get("rol")

    if rol != 'admin':
        # Si no es admin, filtramos solo sus turnos
        pacientes = [p for p in pacientes if p.get("usuario") == usuario_actual]

    # Ordenamos la lista de pacientes por el campo 'nombre'
    pacientes_ordenados = sorted(pacientes, key=lambda x: x["nombre"])
    return render_template("index.html", pacientes=pacientes_ordenados)

#Agregamos paciente
@pacientes_bp.route("/nuevo", methods=["GET", "POST"])
def nuevo_paciente():
    if 'usuario' not in session:
        return redirect(url_for('admin.inicio'))
    
    if request.method == "POST":
        dni = request.form["dni"]
        nombre = request.form["nombre"].strip().capitalize()#Estos son para borrar los espacios extras y poner la primera letra mayuscula
        apellido = request.form["apellido"].strip().capitalize()
        email = request.form["email"].strip().lower()#Borra los espacios extra y primera letra minuscula
        fecha = request.form["fecha"]
        tipo = request.form["tipo"]


        # Validamos el DNI y el email
        # Si no son validos, retornamos un mensaje de error
        if not validarDNI(dni) or not validarMail(email):
            return "Datos invalidos, vuelva a intentarlo"
        

        pacientes = cargar_pacientes()
        # Verificamos si el paciente ya existe
        for paciente in pacientes:
            if paciente["dni"] == dni:
                return "El paciente ya existe"

        usuario_actual = session.get("usuario")  # usamos el nombre de usuario

        # Si no existe, lo agregamos
        pacientes.append({
            "dni": dni,
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "fecha": fecha,
            "tipo": tipo,
            "usuario": usuario_actual
        })
        
        # Guardamos los datos en el .json
        guardar_pacientes(pacientes)
        return redirect(url_for("clientes.index"))  # <-- Esto es lo que te lleva al index
    
    # Si la solicitud es GET, mostramos el formulario
    return render_template("nuevo.html", obras_sociales = obras_sociales)

# Editamos paciente
@pacientes_bp.route("/editar/<dni>", methods=["GET", "POST"])
def editar(dni):
    if 'usuario' not in session:
        return redirect(url_for('admin.inicio'))
    
    pacientes = cargar_pacientes()
    paciente = next((p for p in pacientes if p["dni"] == dni), None)
    if not paciente:
        return "Paciente no encontrado"

     # Solo puede editar el dueño del turno o el admin
    if session.get("rol") != "admin" and paciente.get("usuario") != session.get("usuario"):
        return "No tenés permiso para editar este turno", 403

    if request.method == "POST":
        paciente["dni"] = request.form["dni"]
        paciente["nombre"] = request.form["nombre"].strip().capitalize()
        paciente["apellido"] = request.form["apellido"].strip().capitalize()
        paciente["email"] = request.form["email"].strip().lower()
        paciente["fecha"] = request.form["fecha"]
        paciente["tipo"] = request.form["tipo"]


        guardar_pacientes(pacientes)
        return redirect(url_for("clientes.index"))  # <-- Esto es lo que te lleva al index

    return render_template("editar.html", paciente=paciente, obras_sociales=obras_sociales, id=dni)

#Borramos turno
@pacientes_bp.route("/eliminar/<dni>")
def eliminar(dni):
    if 'usuario' not in session:
        return redirect(url_for('admin.inicio'))

    pacientes = cargar_pacientes()
    pacientes = [p for p in pacientes if p["dni"] != dni]

    if session.get("rol") != "admin" and pacientes.get("usuario") != session.get("usuario"):
        return "No tenés permiso para eliminar este turno", 403

    guardar_pacientes(pacientes)
    return redirect(url_for("clientes.index"))  # <-- Esto es lo que te lleva al index
#Vemos los pacientes

@pacientes_bp.route("/mis_turnos")
def mis_turnos():
    if 'usuario' not in session:
        return redirect(url_for('admin.inicio'))

    usuario_actual = session.get("usuario")
    pacientes = cargar_pacientes()
    
    # Filtramos solo los turnos del usuario logueado
    turnos_usuario = [p for p in pacientes if p.get("usuario") == usuario_actual]

    return render_template("bienvenida.html", pacientes=turnos_usuario)