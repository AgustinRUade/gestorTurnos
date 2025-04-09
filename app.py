from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Lista de turnos - Ejemplo: [ [id, nombre, dia, horario], ... ]
turnos = [
    [1, "Juan Pérez", "Lunes", "10:00"],
    [2, "Ana Gómez", "Martes", "11:30"]
]

# READ - Mostrar todos los turnos
@app.route("/")
def index():
    return render_template("index.html", turnos=turnos)

# CREATE - Formulario para crear turno
@app.route("/nuevo", methods=["GET", "POST"])
def nuevo_turno():
    if request.method == "POST":
        nuevo_id = turnos[-1][0] + 1 if turnos else 1
        nombre = request.form["nombre"]
        dia = request.form["dia"]
        horario = request.form["horario"]
        turnos.append([nuevo_id, nombre, dia, horario])
        return redirect(url_for("index"))
    return render_template("nuevo.html")

# UPDATE - Editar un turno
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_turno(id):
    turno = next((t for t in turnos if t[0] == id), None)
    if request.method == "POST":
        turno[1] = request.form["nombre"]
        turno[2] = request.form["dia"]
        turno[3] = request.form["horario"]
        return redirect(url_for("index"))
    return render_template("editar.html", turno=turno)

# DELETE - Eliminar turno
@app.route("/eliminar/<int:id>")
def eliminar_turno(id):
    global turnos
    turnos = [t for t in turnos if t[0] != id]
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
