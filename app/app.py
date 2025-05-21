from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

administra = ('administracion', '@altaadminis2025')

@app.route('/', methods=['GET', 'POST'])
def inicio():
    mensaje = ''
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        contrasenia = request.form.get('contrasenia')

        if usuario == administra[0] and contrasenia == administra[1]:
            return redirect(url_for('alta'))
        else:
            mensaje = 'Usuario o contraseña incorrectos'

    return render_template('inicio.html', mensaje=mensaje)

@app.route('/alta', methods=['GET', 'POST'])
def alta():
    obras_sociales = ["OSDE", "Swiss Medical", "Galeno", "Medifé", "Omint", "Sancor Salud", 
                      "Federada Salud", "Hospital Italiano", "IOMA", "PAMI", "OSDEPYM", 
                      "Unión Personal", "Luis Pasteur"]

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        dni = request.form.get('dni')
        genero = request.form.get('genero')
        email = request.form.get('email')
        obra_social = request.form.get('obra_social')
        
    return render_template('alta.html', obras_sociales=obras_sociales)