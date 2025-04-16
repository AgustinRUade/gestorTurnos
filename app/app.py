from flask import Flask, render_template, request

app = Flask(__name__)

administra = ['administracion','@altaadminis2025']

@app.route('/', methods = ['POST', 'GET'])
def index():
    return render_template('inicio.html')
def registro():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasenia = request.form['contrasenia']
        if usuario in administra and contrasenia in administra:
            return render_template('index.html')

@app.route('/alta')
def alta():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
