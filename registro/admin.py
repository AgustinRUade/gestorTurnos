from flask import Blueprint, render_template, request, session, url_for, redirect
import re
import json
import os

admin_bp = Blueprint('admin', __name__, template_folder='templates')


PACIENTES_JSON = "pacientes.json"


def cargar_pacientes():
    if not os.path.exists(PACIENTES_JSON):                                         #este es el mismo código acá como en app.py, recurrí a esto como prueba y me funcionó bien, REVER si se quiere hacer esto de otra manera
        return []
    with open(PACIENTES_JSON, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # Si el archivo está corrupto o vacío, retorna una lista vacía
            return []

# Función para guardar la lista de pacientes en el archivo JSON.
# Sobrescribe el archivo con la nueva lista de pacientes.
def guardar_pacientes(pacientes):                                                  #también es un copy de app.py
    try:
        with open(PACIENTES_JSON, "w", encoding="utf-8") as f:
            json.dump(pacientes, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error al guardar pacientes: {e}") #Imprime que hubo un error al guardar los pacientes


administra = ('administracion', '@altaadminis2025') #credenciales para iniciar sesión como administrador, como NO se modifica nunca, y NO se debe modificar nunca, estos datos deben estar en una tupla
usuarios = cargar_pacientes()
paciente = [] #lista de pacientes con su turno, también se vacía al refrescar la página

@admin_bp.route('/', methods=['GET', 'POST'])
def inicio():
    mensaje = ''
    mensaje_tipo = ''
    
    if request.args.get('mensaje') == 'registro_exitoso': 
        mensaje = '¡Registro exitoso! Ya podés iniciar sesión.' #mensaje que se muestra luego de que un usuario se haya registrado correctamente
        mensaje_tipo = 'exito'

    if request.method == 'POST': 
        usuario = request.form.get('usuario')
        contrasenia = request.form.get('contrasenia')

        if usuario == administra[0] and contrasenia == administra[1]:
            session['usuario'] = 'admin'
            session['rol'] = 'admin'
            return redirect(url_for('clientes.index')) #solo si se inicia sesión con credenciales de administrador se direcciona a alta.html

        for user in usuarios: #se recorren todos los usuarios y sus contraseñas de todos los diccionarios (uno por usuario) de la lista 'usuarios'
            if user['email'] == usuario and user['dni'] == contrasenia: #antes había input de usuario y contraseña, ahora el email es el usuario y el dni es la contraseña
                session['usuario'] = usuario
                session['rol'] = 'normal'
                return redirect(url_for('clientes.mis_turnos'))

        mensaje = 'Usuario o contraseña incorrectos'
        mensaje_tipo = 'error'

    return render_template('inicio.html', mensaje=mensaje, mensaje_tipo=mensaje_tipo)




@admin_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    obras_sociales = ["OSDE", "Swiss Medical", "Galeno", "Medifé", "Omint", "Sancor Salud", 
                      "Federada Salud", "Hospital Italiano", "IOMA", "PAMI", "OSDEPYM", 
                      "Unión Personal", "Luis Pasteur"] #lista de obras sociales
    mensaje = '' #variable de texto vacía para que se le pueda asignar mensaje que le corresponda dependiendo del camino del usuario
    if request.method == 'POST':
        nombre = request.form.get('nombre') #acá comienza la captura de los datos que el usuario ingresa en los input. Solicita (request) optener (get) lo que ingresa el usuario para registrarse
        apellido = request.form.get('apellido')
        dni = request.form.get('dni')
        genero = request.form.get('genero')
        email = request.form.get('email')
        obra_social = request.form.get('obra_social')
        if not validarDNI(dni): #se valida que el formato de DNI sea correcto
            mensaje = 'DNI inválido. Debe contener solo números y tener entre 7 y 8 dígitos.'
            return render_template('registro.html', obras_sociales=obras_sociales, mensaje=mensaje)
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$' #variable para formato de mail
        if not re.match(email_regex, email): #se valida que formato de MAIL sea correcto
            mensaje = 'Email inválido. Ingrese un formato correcto.'
            return render_template('registro.html', obras_sociales=obras_sociales, mensaje=mensaje)
        for user in usuarios: #se valida que el dni con el que se quiere registrar el usuario no esté ya en la matriz con los usuarios existentes
            if user['dni'] == dni:
                mensaje = 'El DNI ya está registrado.'
                return render_template('registro.html', obras_sociales=obras_sociales, mensaje=mensaje)
        for user in usuarios: #se valida que el mail con el que se quiere registrar el usuario no esté ya en la matriz con los usuarios existentes
            if user['email'] == email:
                mensaje = 'Este correo electrónico ya está registrado.'
                return render_template('registro.html', obras_sociales=obras_sociales, mensaje=mensaje)
        usuarios.append({ #se guarda el resgistro de un usuario nuevo
            'nombre': nombre,
            'apellido': apellido,
            'dni': dni, #MODIFICACIÓN, ahora el DNI pasa como contraseña
            'genero': genero,
            'email': email, #MODIFICACIÓN, ahora el mail pasa como nombre de usuario
            'obra_social': obra_social, 
        })
        guardar_pacientes(usuarios)
        mensaje = '¡Registro exitoso! Ya podés iniciar sesión.'
        return redirect(url_for('admin.inicio', mensaje='registro_exitoso'))
    
    return render_template('registro.html', obras_sociales=obras_sociales, mensaje=mensaje)


@admin_bp.route('/alta', methods=['GET', 'POST']) #por ahora está pensada como ruta para demostrar funcionalidad, solo iniciando sesión con usuario y contraseña de administrador se dirige a esta ruta
def alta():
    obras_sociales = ["OSDE", "Swiss Medical", "Galeno", "Medifé", "Omint", "Sancor Salud", 
                      "Federada Salud", "Hospital Italiano", "IOMA", "PAMI", "OSDEPYM", 
                      "Unión Personal", "Luis Pasteur"] #lista de obras sociales para que administrador pueda registrar un paciente
    return render_template('alta.html', obras_sociales=obras_sociales)


@admin_bp.route('/bienvenida') #también pensada como ruta para mostrar funcionalidad, solo iniciando sesión con usuario y contraseña que NO sea de administrador se dirige a esta ruta
def bienvenida():
    nombre = request.args.get('nombre')
    return render_template('bienvenida.html', nombre=nombre, pacientes=paciente)

@admin_bp.route("/logout")
def logout():
    session.clear()  # borra todos los datos de sesión
    return redirect(url_for("admin.inicio"))

@admin_bp.route('/turnocliente', methods=['GET', 'POST'])
def turnocliente():

    obras_sociales = ["OSDE", "Swiss Medical", "Galeno", "Medifé", "Omint", "Sancor Salud", 
                      "Federada Salud", "Hospital Italiano", "IOMA", "PAMI", "OSDEPYM", 
                      "Unión Personal", "Luis Pasteur"]
    
    if request.method == 'POST':
        dni = request.form['user_dni']
        nombre = request.form['user_nombre']
        obra_social = request.form['tipo']
        fecha = request.form['user_fecha']

        paciente.append({
            'dni': dni,
            'nombre': nombre,
            'obra_social': obra_social,
            'fecha': fecha
        })

        return redirect(url_for('admin.bienvenida'))  # vuelve a misturnos.html
    return render_template('turnocliente.html', obras_sociales=obras_sociales)


@admin_bp.route('/eliminar/<dni>', methods=['GET'])
def eliminar(dni):
    global paciente  # usamos la lista global

    paciente_encontrado = next((p for p in paciente if p["dni"] == dni), None)

    if not paciente_encontrado:
        return "Paciente no encontrado", 404

    paciente.remove(paciente_encontrado)  # se elimina automáticamente

    return redirect(url_for('admin.bienvenida'))  # redirige después de eliminar

def validarDNI(dni):
    return dni.isdigit() and len(dni) == 8
