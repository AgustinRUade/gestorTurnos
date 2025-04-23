from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

administra = ['administracion','@altaadminis2025']

@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasenia = request.form['contrasenia']
        if usuario in administra and contrasenia in administra:
            return redirect(url_for('alta'))
    return render_template('inicio.html')

@app.route('/alta')
def alta():
    obras_sociales = ["OSDE", "Swiss Medical", "Galeno", "Medifé", "Omint", "Sancor Salud", "Federada Salud", "Hospital Italiano", "IOMA", "PAMI", "OSDEPYM", "Unión Personal","Luis Pasteur"]
    return render_template('index.html', obras_sociales=obras_sociales)

if __name__ == '__main__':
    app.run(debug=True)
