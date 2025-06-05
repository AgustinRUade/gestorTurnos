from flask import Flask, render_template, request, url_for, redirect, session
import re #este import ayuda a la validación de datos como mail y/o dni
from datetime import timedelta #import de tiempo, fechas, para establecer el tiempo de duración de la sesión en este caso
import json
import os

app = Flask(__name__) #creación de app tipo Flask

USUARIOS_JSON = os.path.join(os.path.dirname(__file__), 'usuarios.json')

def cargar_pacientes():
    if not os.path.exists(USUARIOS_JSON):
        return []
    with open(USUARIOS_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def guardar_pacientes(lista):
    with open(USUARIOS_JSON, 'w', encoding='utf-8') as f:
        json.dump(lista, f, ensure_ascii=False, indent=4)

app.secret_key = 'contra_se_123'  #clave necesaria para usar sesiones
app.permanent_session_lifetime = timedelta(days=7) #se establece el tiempo por el cual la sesión se mantiene iniciada, en este caso establecí 7 días



administra = ('administracion', '@altaadminis2025') # credenciales para iniciar sesión como administrador

@app.route('/', methods=['GET', 'POST'])
def inicio():
    mensaje = ''
    mensaje_tipo = ''
    if request.args.get('mensaje') == 'registro_exitoso':
        mensaje = '¡Registro exitoso! Ya podés iniciar sesión.' #mensaje que se muestra luego de que un usuario se haya registrado correctamente
        mensaje_tipo = 'exito'
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        contrasenia = request.form.get('contrasenia')
        mantener_sesion = request.form.get('mantener_sesion') #captura valor del checkbox que se encuentra en inicio.html
        if mantener_sesion == 'on': #si se marca el checkbox la variable mantener_sesion tiene el valor 'on'
            session.permanet = True #si el valor es 'on', la sesión persiste
        else: #si el checkbox no se marca, entonces la variable mantener_sesion NO tiene el valor 'on', por lo tanto se ejecuta el else
            session.permanent = False #si el valor NO es 'on', la sesión NO persiste
        if usuario == administra[0] and contrasenia == administra[1]: 
            session['admin'] = True  #seguridad, se confirma que el administrador inició sesión
            return redirect(url_for('buscar_paciente')) #solo si se inicia sesión con credenciales de administrador se direcciona a la función buscar_paciente
        for user in cargar_pacientes(): #se recorren todos los usuarios y sus contraseñas de todos los diccionarios (uno por usuario) de la lista 'usuarios'
            if user['usuario'] == usuario and user['contrasenia'] == contrasenia:
                session.permanent = mantener_sesion #se pensó la permanencia de la sesión SOLO en la el caso de inicio de sesión de un usuario común, REVER si se quiere también esto para el usuario administrador
                session['usuario'] = user['usuario']
                return redirect(url_for('bienvenida', nombre=user['nombre']))
        mensaje = 'Usuario o contraseña incorrectos'
        mensaje_tipo = 'error'
    return render_template('inicio.html', mensaje=mensaje, mensaje_tipo=mensaje_tipo)

@app.route('/buscar_paciente', methods=['GET']) #a esta ruta SOLO PUEDE ACCEDER EL ADMINISTRADOR para buscar un paciente por su DNI
def buscar_paciente():
    if not session.get('admin'): #seguridad, se verifica que quién entra a esta ruta sea el usuario administrador, si no lo es se lo dirige al inicio
        return redirect(url_for('inicio'))
    dni = request.args.get('dni')  #obtiene el parámetro 'dni' desde la URL (formulario GET)
    pacientes = cargar_pacientes()
    encontrado = None #variable con contenido False, si se encuentra un paciente se lo guarda en esta variable
    if dni:
        for paciente in pacientes: #se recorre la lista de pacientes (usuarios) para encontrar el paciente que tenga el DNI ingresado
            if paciente["dni"] == dni:
                encontrado = paciente
                break #si se encuentra el paciente se sale del bucle
        mensaje = None if encontrado else "Paciente no encontrado." #mensaje de error si no se encuentra ningún paciente
        return render_template("buscar.html", paciente=encontrado, mensaje=mensaje)
    return render_template("buscar.html", paciente=None, mensaje=None)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    obras_sociales = ["OSDE", "Swiss Medical", "Galeno", "Medifé", "Omint", "Sancor Salud",
                      "Federada Salud", "Hospital Italiano", "IOMA", "PAMI", "OSDEPYM",
                      "Unión Personal", "Luis Pasteur"] #lista de obras sociales, se muestra en el formulario de registro de nuevo usuario
    mensaje = '' #variable de texto vacía para que se le pueda asignar mensaje que le corresponda dependiendo del camino del usuario
    if request.method == 'POST':
        nombre = request.form.get('nombre') #acá comienza la captura de los datos que el usuario ingresa en los input. Solicita (request) optener (get) lo que ingresa el usuario para registrarse
        apellido = request.form.get('apellido')
        dni = request.form.get('dni')
        genero = request.form.get('genero')
        email = request.form.get('email')
        obra_social = request.form.get('obra_social')
        usuario = request.form.get('usuario')
        contrasenia = request.form.get('contrasenia')
        usuarios = cargar_pacientes()  # <-- AGREGA ESTA LÍNEA AQUÍ
        if not dni.isdigit() or not (7 <= len(dni) <= 8): #se valida el formato del DNI, númerico y entre 7 y 8 digitos
            mensaje = 'DNI inválido. Debe contener solo números y tener entre 7 y 8 dígitos.'
            return render_template('registro.html', obras_sociales=obras_sociales, mensaje=mensaje)
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$' #validación formato de mail
        if not re.match(email_regex, email): 
            mensaje = 'Email inválido. Ingrese un formato correcto.'
            return render_template('registro.html', obras_sociales=obras_sociales, mensaje=mensaje)
        for user in usuarios:  #se valida que el nombre de usuario con el que se quiere registrar el usuario no esté ya en la matriz con los usuarios existentes
            if user['usuario'] == usuario:
                mensaje = 'El nombre de usuario ya está registrado.'
                return render_template('registro.html', obras_sociales=obras_sociales, mensaje=mensaje)
            if user['dni'] == dni: #se valida que el dni con el que se quiere registrar el usuario no esté ya en la matriz con los usuarios existentes
                mensaje = 'El DNI ya está registrado.'
                return render_template('registro.html', obras_sociales=obras_sociales, mensaje=mensaje)
            if user['email'] == email: #se valida que el mail con el que se quiere registrar el usuario no esté ya en la matriz con los usuarios existentes
                mensaje = 'Este correo electrónico ya está registrado.'
                return render_template('registro.html', obras_sociales=obras_sociales, mensaje=mensaje)
        usuarios.append({ #se guarda el resgistro de un usuario nuevo
            'nombre': nombre,
            'apellido': apellido,
            'dni': dni,
            'genero': genero,
            'email': email,
            'obra_social': obra_social,
            'usuario': usuario,
            'contrasenia': contrasenia
        })
        guardar_pacientes(usuarios)
        return redirect(url_for('inicio', mensaje='registro_exitoso'))
    return render_template('registro.html', obras_sociales=obras_sociales, mensaje=mensaje)

@app.route('/bienvenida')
def bienvenida():
    nombre = request.args.get('nombre')
    return render_template('bienvenida.html', nombre=nombre)

if __name__ == '__main__':
    app.run(debug=True)
