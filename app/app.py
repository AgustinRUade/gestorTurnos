from flask import Flask, render_template, request, url_for, redirect
import re #este import ayuda a la validación de datos como mail y/o dni

app = Flask(__name__) #creación de app tipo Flask

administra = ('administracion', '@altaadminis2025') #credenciales para iniciar sesión como administrador, como NO se modifica nunca, y NO se debe modificar nunca, estos datos deben estar en una tupla
usuarios = [] #lista donde se guardan los diccionarios, por supuesto no es una base de datos, solo almacena en ram, entonces cuando se refresca la página la lista se vacía completamente

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

        if usuario == administra[0] and contrasenia == administra[1]:
            return redirect(url_for('alta')) #solo si se inicia sesión con credenciales de administrador se direcciona a alta.html

        for user in usuarios: #se recorren todos los usuarios y sus contraseñas de todos los diccionarios (uno por usuario) de la lista 'usuarios'
            if user['usuario'] == usuario and user['contrasenia'] == contrasenia:
                return redirect(url_for('bienvenida', nombre=user['nombre']))

        mensaje = 'Usuario o contraseña incorrectos'
        mensaje_tipo = 'error'

    return render_template('inicio.html', mensaje=mensaje, mensaje_tipo=mensaje_tipo)




@app.route('/registro', methods=['GET', 'POST'])
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
        usuario = request.form.get('usuario')
        contrasenia = request.form.get('contrasenia')
        if not dni.isdigit() or not (7 <= len(dni) <= 8): #se valida que el formato de DNI sea correcto
            mensaje = 'DNI inválido. Debe contener solo números y tener entre 7 y 8 dígitos.'
            return render_template('registro.html', obras_sociales=obras_sociales, mensaje=mensaje)
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$' #variable para formato de mail
        if not re.match(email_regex, email): #se valida que formato de MAIL sea correcto
            mensaje = 'Email inválido. Ingrese un formato correcto.'
            return render_template('registro.html', obras_sociales=obras_sociales, mensaje=mensaje)
        for user in usuarios: #se valida que el nombre de usuario con el que se quiere registrar el usuario no esté ya en la matriz con los usuarios existentes
            if user['usuario'] == usuario:
                mensaje = 'El nombre de usuario ya está registrado.'
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
            'dni': dni,
            'genero': genero,
            'email': email,
            'obra_social': obra_social,
            'usuario': usuario,
            'contrasenia': contrasenia
        })
        mensaje = '¡Registro exitoso! Ya podés iniciar sesión.'
        return redirect('inicio.html', mensaje='registro_exitoso')
    
    return render_template('registro.html', obras_sociales=obras_sociales, mensaje=mensaje)


@app.route('/alta', methods=['GET', 'POST']) #por ahora está pensada como ruta para demostrar funcionalidad, solo iniciando sesión con usuario y contraseña de administrador se dirige a esta ruta
def alta():
    obras_sociales = ["OSDE", "Swiss Medical", "Galeno", "Medifé", "Omint", "Sancor Salud", 
                      "Federada Salud", "Hospital Italiano", "IOMA", "PAMI", "OSDEPYM", 
                      "Unión Personal", "Luis Pasteur"] #lista de obras sociales para que administrador pueda registrar un paciente
    return render_template('alta.html', obras_sociales=obras_sociales)


@app.route('/bienvenida') #también pensada como ruta para mostrar funcionalidad, solo iniciando sesión con usuario y contraseña que NO sea de administrador se dirige a esta ruta
def bienvenida():
    nombre = request.args.get('nombre')
    return render_template('bienvenida.html', nombre=nombre)

if __name__ == '__main__': #activación de debugging
    app.run(debug=True)
