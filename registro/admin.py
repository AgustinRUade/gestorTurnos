from flask import Blueprint, render_template, request, session, url_for, redirect
from funciones_comunes import registrar_log, registrar_error, validarDNI, validarMail, cargar_pacientes, guardar_pacientes, PACIENTES_JSON #importamos las funciones de registro de log y error, validación de dni y de email, desde funciones_comunes.py
#importación de funciones_comunes.py, tiene funciones que se usan tanto acá en admin.py como en app.py de la carpeta administrador: por esto decidí ponerlo en un archivo aparte, y además ahí estan las escrituras al .log y validaciones logicas, lo que facilita la prueba en el pytest



admin_bp = Blueprint('admin', __name__, template_folder='templates')


administra = ('administracion', '@altaadminis2025') #credenciales para iniciar sesión como administrador, como NO se modifica nunca, y NO se debe modificar nunca, estos datos deben estar en una tupla
usuarios = cargar_pacientes() #
paciente = [] #lista de pacientes con su turno, también se vacía al refrescar la página

@admin_bp.route('/', methods=['GET', 'POST'])
def inicio():
    if 'usuario' in session: #verifica si hay una sesión iniciada, si la hay, redirige a la página de mis turnos
        if session.get('rol') == 'normal':
            return redirect(url_for('clientes.mis_turnos'))
    mensaje = '' #variable de texto vacía para que se le pueda asignar mensaje que le corresponda dependiendo del camino del usuario
    mensaje_tipo = '' #variable de texto vacia que dependiendo de lo que sucede en el sistema puede tomar valor "error" o "exito"
    if request.args.get('mensaje') == 'registro_exitoso': 
        mensaje = '¡Registro exitoso! Ya podés iniciar sesión.' #mensaje que se muestra luego de que un usuario se haya registrado correctamente
        mensaje_tipo = 'exito'

    if request.method == 'POST': #sucede cuando el usuario envía el formulario de inicio de sesión
        usuario = request.form.get('usuario') #toma el valor del input 'usuario' del formulario de inicio de sesión, ES EL EMAIL
        #RECORDARE QUE ANTES se usaba un input PROPIO de usuario y otro PROPIO de contraseña, ahora se usa el email como usuario y el dni como contraseña
        contrasenia = request.form.get('contrasenia') #toma el valor del input 'contrasenia' del formulario de inicio de sesión, ES EL DNI
        mantener_sesion = request.form.get('mantener_sesion') #variable que toma el valor del input 'mantener_sesion' del formulario de inicio de sesión, si está marcado, la sesión se mantendrá iniciada por 7 días, sino, se cerrará al cerrar el navegador
        if usuario == administra[0] and contrasenia == administra[1]: #validación de las credenciales del administrador, SOLO si el valor del indice 0 de la tupla administra es igual a lo ingresado en el input de usuario y SOLO SI el valor del indice 1 de la tupla administra es igual a lo ingresado en el input de contraseña, entonces se inicia sesión como administrador
            session['usuario'] = 'admin' #
            session['rol'] = 'admin'
            registrar_log(f"[INICIO SESIÓN] Usuario '{usuario}' inició sesión como administrador.")  #se registra en el archivo .log inicio de sesión del usuario administrador
            return redirect(url_for('clientes.index')) #solo si se inicia sesión con credenciales de administrador se direcciona ACÁ
        for user in usuarios: #se recorren todos los usuarios y sus contraseñas de todos los diccionarios (uno por usuario) de la lista 'usuarios'
            if user['email'] == usuario and user['dni'] == contrasenia: #antes había input de usuario y contraseña, ahora el email es el usuario y el dni es la contraseña
                session['usuario'] = usuario
                session['rol'] = 'normal'
                session.permanent = True if mantener_sesion == 'on' else False #SI el checkbox está marcado la variable toma el valor ON, y hace que la sesión permanente sea de valor TRUE, SINO, si el checkbox no está marcado la variable no toma el valor ON, y entonces hace que la sesión permanente sea de valor FALSE, es decir, que la sesión se cerrará al cerrar el navegador
                registrar_log(f"[INICIO SESIÓN] Usuario '{usuario}' inició sesión.") #se registra en el .log cuando un usuario común inicia sesión
                return redirect(url_for('clientes.mis_turnos')) #un usuario común inicia sesión y es dirigido a la pantalla de sus turnos
        #si no se encuentra el usuario o la contraseña es incorrecta, se muestra un mensaje de error
        mensaje = 'Usuario o contraseña incorrectos'
        mensaje_tipo = 'error'
        registrar_log(f"[ERROR INICIO SESIÓN] Usuario '{usuario}' intentó iniciar sesión y falló.")  #se registra en el archivo .log que quién intentó iniciar sesión (se captura el dato del input de usuario y se lo registra en el .log) no logró hacerlo
    return render_template('inicio.html', mensaje=mensaje, mensaje_tipo=mensaje_tipo)




@admin_bp.route('/registro', methods=['GET', 'POST'])
def registro(): #Resgistro de usuario nuevo desde la interfaz de login
    obras_sociales = ["OSDE", "Swiss Medical", "Galeno", "Medifé", "Omint", "Sancor Salud", 
                      "Federada Salud", "Hospital Italiano", "IOMA", "PAMI", "OSDEPYM", 
                      "Unión Personal", "Luis Pasteur"] #lista de obras sociales
    mensaje = '' #variable de texto vacía para que se le pueda asignar mensaje que le corresponda dependiendo del camino del usuario
    if request.method == 'POST': #sucede cuando el usuario envía el formulario de registro
        nombre = request.form.get('nombre') #acá comienza la captura de los datos que el usuario ingresa en los input. Solicita (request) optener (get) lo que ingresa el usuario para registrarse
        apellido = request.form.get('apellido')
        dni = request.form.get('dni')
        genero = request.form.get('genero')
        email = request.form.get('email')
        obra_social = request.form.get('obra_social')
        if not validarDNI(dni): #se valida que el formato de DNI sea correcto, esto es de la función validarDNI que esta en el archivo funciones_comunes.py, es importado a este documento en la segunda línea de este archivo actual
            mensaje = 'DNI inválido. Debe contener solo números y tener entre 7 y 8 dígitos.' #mensaje SI NO se cumple el formato
            return render_template('registro.html', obras_sociales=obras_sociales, mensaje=mensaje) 
        if not validarMail(email): #se valida que formato de MAIL sea correcto, esto, igual que validarDNI, está en el archivo funciones_comunes.py, por lo tanto es una función importada
            mensaje = 'Email inválido. Ingrese un formato correcto.' #mensaje SI NO se cumple el formato
            return render_template('registro.html', obras_sociales=obras_sociales, mensaje=mensaje)
        for user in usuarios: #se valida que el dni con el que se quiere registrar el usuario no esté ya en la matriz con los usuarios existentes
            if user['dni'] == dni: #se verifica si el dni con el que se intenta registrar el usuario está ya registrado
                mensaje = 'El DNI ya está registrado.' #mensaje si se intenta registrar un usuario con un dni que ya está registrado
                return render_template('registro.html', obras_sociales=obras_sociales, mensaje=mensaje)
        for user in usuarios: 
            if user['email'] == email: #se valida que el mail con el que se quiere registrar el usuario no esté ya registrado
                mensaje = 'Este correo electrónico ya está registrado.' #mensaje si el email ya está registrado
                return render_template('registro.html', obras_sociales=obras_sociales, mensaje=mensaje)
        usuarios.append({ #se guarda el registro de un usuario nuevo
            'nombre': nombre,
            'apellido': apellido,
            'dni': dni, #MODIFICACIÓN, ahora el DNI pasa como contraseña
            'genero': genero,
            'email': email, #MODIFICACIÓN, ahora el mail pasa como nombre de usuario
            'obra_social': obra_social, 
        })
        guardar_pacientes(usuarios)
        registrar_log(f"[REGISTRO] Usuario '{email}' se registró exitosamente.")  #se registra en el archivo .log que un usuario nuevo se registró
        mensaje = '¡Registro exitoso! Ya podés iniciar sesión.' #mensaje que se muestra en la pantalla de login luego de que un usuario se registra exitosamente
        return redirect(url_for('admin.inicio', mensaje='registro_exitoso'))
    
    return render_template('registro.html', obras_sociales=obras_sociales, mensaje=mensaje)

#VERIFICAR SI ESTO DIRIGE A UNA RUTA
@admin_bp.route('/alta', methods=['GET', 'POST'])
def alta():
    obras_sociales = ["OSDE", "Swiss Medical", "Galeno", "Medifé", "Omint", "Sancor Salud", 
                      "Federada Salud", "Hospital Italiano", "IOMA", "PAMI", "OSDEPYM", 
                      "Unión Personal", "Luis Pasteur"] #lista de obras sociales para que administrador pueda registrar un paciente
    return render_template('alta.html', obras_sociales=obras_sociales)

#VERIFICAR SI ESTO DIRIGE A UNA RUTA
@admin_bp.route('/bienvenida')
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
        registrar_log(f"[TURNO] Paciente {nombre} (DNI: {dni}) ha agendado un turno para el {fecha}.") #se registra en el .log cuando un usuario se asigna un turno
        return redirect(url_for('admin.bienvenida'))  # vuelve a misturnos.html
    return render_template('turnocliente.html', obras_sociales=obras_sociales)


@admin_bp.route('/eliminar/<dni>', methods=['GET'])
def eliminar(dni):
    global paciente  # usamos la lista global

    paciente_encontrado = next((p for p in paciente if p["dni"] == dni), None)

    if not paciente_encontrado:
        return "Paciente no encontrado", 404

    paciente.remove(paciente_encontrado)  # se elimina automáticamente
    registrar_log(f"[ELIMINACIÓN] Paciente con DNI {dni} ha sido eliminado.") #se registra en el archivo .log que se eliminó un paciente
    return redirect(url_for('admin.bienvenida'))  # redirige después de eliminar


