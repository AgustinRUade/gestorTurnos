from flask import Flask, render_template
app = Flask(__name__)

turnos = [
    ["Manuel Perez", "Odontologo", "Martes", "10:00"],
    ["Marcelo Meza", "Oftalmologo", "Miercoles", "13:00"],
    ["Nahuel Mendoza", "Otorrino", "Viernes", "12:30"]
]

@app.route('/')
def index():
    return render_template('index.html', turnos = turnos)

if __name__ == '__main__':
    app.run(debug = True)