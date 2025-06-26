#Aca generamos la matriz de turnos (de momento vacia)
#Creamos el CRUD para crear, ver, editar y borrar los turnos
from flask import Blueprint, render_template, request, redirect, session, url_for
from funciones_comunes import registrar_log, registrar_error, validarDNI, validarMail, cargar_pacientes, guardar_pacientes, PACIENTES_JSON #importamos las funciones de registro de log y error, validación de dni y de email, carga  y guardado de pacientes dque están en funciones_comunes.py

pacientes_bp = Blueprint('clientes', __name__, url_prefix="/pacientes", template_folder="templates") 

PACIENTES_FILE = "pacientes.json" #verificar si es necesario que esta variable siga existiendo acá


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

#Ruta princiapl
@pacientes_bp.route("/")
def index():
    
    if 'usuario' not in session:
        return redirect(url_for('admin.inicio')) # Esto hace que alguien no logueado pueda ingresar
    
    # Cargamos los datos del .json
    pacientes = cargar_pacientes()
    usuario_actual = session.get("usuario")
    rol = session.get("rol")
    for p in pacientes:          
        print(" -", type(p), p) #tuve un error antes, como en el lambda se pide por "nombre", agregué esto para verificar que exista el campo nombre en el json
    for p in pacientes:
        if "nombre" not in p:
            registrar_error(f"[ADVERTENCIA] Paciente sin campo 'nombre': {p}")  #se registra un error en archivo.log si algún paciente no tiene el campo 'nombre' con datos

    if rol != 'admin':
        # Si no es admin, filtramos solo sus turnos
        pacientes = [p for p in pacientes if p.get("usuario") == usuario_actual]
    # Ordenamos la lista de pacientes por el campo 'nombre'
    pacientes_ordenados = sorted(pacientes, key=lambda x: x["nombre"])
    return render_template("index.html", pacientes=pacientes_ordenados)

@pacientes_bp.route('/buscar_paciente', methods=['GET']) #a esta ruta SOLO PUEDE ACCEDER EL ADMINISTRADOR para buscar un paciente por su DNI
def buscar_paciente():
    dni = request.args.get('dni')  #obtiene el parámetro 'dni' desde la URL (formulario GET)
    pacientes = cargar_pacientes()
    encontrado = None #variable con contenido None, si se encuentra un paciente se lo guarda en esta variable
    matriz_busqueda = []
    if dni:
        registrar_log(f"[BÚSQUEDA] Usuario '{session.get('usuario')}' buscó paciente con DNI: {dni}")  #se registra en el archivo .log que se buscó un paciente y se registra qué dni se buscó
        for paciente in pacientes: #se recorre la lista de pacientes (usuarios) para encontrar el paciente que tenga el DNI ingresado
            if paciente["dni"] == dni:
                registrar_log(f"[ENCONTRADO] Paciente encontrado: {paciente['apellido']}, {paciente['nombre']}. (DNI: {dni})")  #se registra en el archivo .log que se encontró un paciente con el dni ingresado, en el log. se registra nombre, apellido y dni
                encontrado = paciente
                break #si se encuentra el paciente se sale del bucle
        if encontrado:
            matriz_busqueda = [ #de RAM, cuando se busca otro paciente la matriz se vacía del contenido anterior y se rellena con los datos del paciente encontrado actualmente
                ["Nombre", encontrado.get("nombre", "")],
                ["Apellido", encontrado.get("apellido", "")],
                ["DNI", encontrado.get("dni", "")],
                ["Género", encontrado.get("genero", "")],
                ["Email", encontrado.get("email", "")],
                ["Obra Social", encontrado.get("obra_social", "")]
            ] #si se encuentra el paciente, se crea una matriz con los datos del paciente encontrado, si no se encuentra el dato, se deja vacío
        else:
            registrar_log(f"[NO ENCONTRADO] Paciente no encontrado con DNI: {dni}") #se registra en el archivo .log que el paciente que se intentó buscar no fue encontrado, en el .log se registra el dni que no se encontró
        mensaje = None if encontrado else "Paciente no encontrado." #mensaje de error si no se encuentra ningún paciente
        return render_template('buscar_paciente.html', matriz=matriz_busqueda, mensaje=mensaje)
    return render_template('buscar_paciente.html', matriz=None, mensaje=None)


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
        obra_social = request.form["obra_social"]

        # Validamos el DNI y el email
        # Si no son validos, retornamos un mensaje de error
        if not validarDNI(dni) or not validarMail(email):
            return "Datos invalidos, vuelva a intentarlo"
        

        pacientes = cargar_pacientes()
        usuario_actual = session.get("usuario")  #usamos el nombre de usuario
        # Verificamos si el paciente ya existe
        for paciente in pacientes:
            if paciente["dni"] == dni:
                registrar_log(f"[DENEGADO] Usuario '{usuario_actual}' intentó registrar paciente ya existente DNI {dni}") #se registra en el archivo .log que se intentó registrar un paciente ya existente, se deja registro del dni
                return "El paciente ya existe"

        

        # Si no existe, lo agregamos
        pacientes.append({
            "dni": dni,
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "obra_social": obra_social,
            "usuario": usuario_actual
        })
        
        try:
            guardar_pacientes(pacientes) #Guardamos los datos en el .json
            registrar_log(f"[REGISTRO] Usuario '{usuario_actual}' registró nuevo paciente: {apellido}, {nombre}. (DNI: {dni})")  #se deja registro en el archivo .log que se registró un nuevo paciente, se registra en el .log apellido, nombre y dni del paciente nuevo
        except Exception as e: #error de registro de paciente como alias "e", se registra en el .log el error según la función registrar_error que está en el archivo funciones_comunes
            registrar_error(e)
            return "Error inesperado al registrar paciente"
            
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
        paciente["tipo"] = request.form["tipo"]
        try:
            guardar_pacientes(pacientes)
            registrar_log(f"[EDICIÓN] Usuario '{session.get('usuario')}' editó paciente: {paciente['apellido']}, {paciente['nombre']}. (DNI: {paciente['dni']})")  #se deja registro en el archivo .log que se editó un paciente, se muestra apellido, nombre y dni
        except Exception as e:
            registrar_error(e) #se registro en el archivo .log si hubo un error al guardar los datos de edición
            return "Error inesperado al editar paciente"

        return redirect(url_for("clientes.index"))  #redirigimos al index después de editar

    return render_template("editar.html", paciente=paciente, obras_sociales=obras_sociales, id=dni)

#Borramos turno
@pacientes_bp.route("/eliminar/<dni>")
def eliminar(dni):
    if 'usuario' not in session:
        return redirect(url_for('admin.inicio'))

    pacientes = cargar_pacientes()
    paciente = next((p for p in pacientes if p["dni"] == dni), None)
    if not paciente:
        return "Paciente no encontrado"    
    if session.get("rol") != "admin" and paciente.get("usuario") != session.get("usuario"):
        return "No tenés permiso para eliminar este turno", 403
    pacientes = [p for p in pacientes if p["dni"] != dni]
    try:
        registrar_log(f"[ELIMINACIÓN] Usuario '{session.get('usuario')}' eliminó paciente: {paciente['apellido']}, {paciente['nombre']}. (DNI: {paciente['dni']})")  #se deja registro en el archivo .log que se eliminó un paciente, dejando registro en el .log del apellido, nombre y dni del paciente borrado
         # Si hubo un error al guardar, se registra en el archivo .log
        guardar_pacientes(pacientes)
    except Exception as e:
        registrar_error(e) #de haber ocurrido un error al querer eliminar un paciente, se registra en el archivo .log
        return "Error inesperado al eliminar paciente"

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