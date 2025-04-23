#Aca generamos la matriz de turnos (de momento vacia)
#Creamos el CRUD para crear, ver, editar y borrar los turnos
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

#Matriz de turnos
turnos = []

#Hacemos que el dni sea de 8 digitos y que se asegure son sumeros
def validarDNI(dni):
    return dni.isdigit() and len(dni) == 8

#En este vemos que tenga el @
def validarMail(email):
    return "@" in email

#Ruta princiapl
@app.route("/")
def index():
    turnosOrdenados = sorted(turnos, key = lambda x: x[1]) #Ordenamos la matriz por nombres
    return render_template("index.html", turnos = turnosOrdenados)

#Creamos turno
@app.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "POST":
        dni = request.form["dni"]
        nombre = request.form["nombre"].strip().capitalize()#Estos son para borrar los espacios extras y poner la primera letra mayuscula
        email = request.form["email"].strip().lower()#Borra los espacios extra y primera letra minuscula
        tipo = request.form["tipo"]

        if not validarDNI(dni) or not validarMail(email):
            return "Datos invalidos, vuelva a intentarlo"
        
        turnos.append([dni, nombre, email, tipo])
        return redirect(url_for("index"))
    
    return render_template("nuevo.html")

#Editamos turno
@app.route("/editar/<dni>", methods = ["GET", "POST"])
def editar(dni):
    turno = next((t for t in turnos if t[0] == dni), None)
    if request.method == "POST":
        turno[0] = request.form["dni"]
        turno[1] = request.form["nombre"].strip().capitalize()
        turno[2] = request.form["email"].strip().lower()
        turno[3] = request.form["tipo"]
        return redirect("/")
    
    return render_template("editar.html", turno = turno, id = dni)

#Borramos turno
@app.route("/eliminar/<dni>")
def eliminar(dni):
    global turnos
    turnos = [t for t in turnos if t[0] != dni]
    return redirect("/")

if __name__ == "__main__":
    app.run(debug = True)