#Aca generamos la matriz de turnos (de momento vacia)
#Creamos el CRUD para crear, ver, editar y borrar los turnos
from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)


PACIENTES_FILE = "pacientes.json"

# Función para cargar la lista de pacientes desde el archivo JSON.
# Si el archivo no existe o está vacío, devuelve una lista vacía.
def cargar_pacientes():
    try:
        if not os.path.exists(PACIENTES_FILE):
            return []
        with open(PACIENTES_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # Si el archivo está corrupto o vacío, retorna una lista vacía
                return []
    except Exception as e:
        return f"Error al cargar los pacientes: {e}"

# Función para guardar la lista de pacientes en el archivo JSON.
# Sobrescribe el archivo con la nueva lista de pacientes.
def guardar_pacientes(pacientes):
    try:
        with open(PACIENTES_FILE, "w", encoding="utf-8") as f:
            json.dump(pacientes, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error al guardar pacientes: {e}") #Imprime que hubo un error al guardar los pacientes


#Lista de obras sociales
#Esta lista es para que el usuario pueda elegir la obra social
obras_sociales = [
    "IOMA",
    "OSDE",
    "Swiss Medical",
    "Galeno",
    "Omint",
    "Medicus",
    "Federada Salud",
    "OSPIP",
    "PAMI",
    "OSUTHGRA"
]

#Hacemos que el dni sea de 8 digitos y que se asegure son sumeros
def validarDNI(dni):
    if not dni.isdigit() and len(dni) == 8:
        raise ValueError("dni invalido")
    return True
#En este vemos que tenga el @
def validarMail(email):
    if "@" not in email or "." not in email:
        raise ValueError("email invalido")
    return True

#Ruta principal
@app.route("/")
def index():
    # Cargamos los datos del .json
    pacientes = cargar_pacientes()
    # Ordenamos la lista de pacientes por el campo 'nombre'
    pacientes_ordenados = sorted(pacientes, key=lambda x: x["nombre"])
    return render_template("index.html", pacientes=pacientes_ordenados)

#Agregamos paciente
@app.route("/nuevo", methods=["GET", "POST"])
def nuevo_paciente():
    
    if request.method == "POST":
        dni = request.form["dni"]
        nombre = request.form["nombre"].strip().capitalize()#Estos son para borrar los espacios extras y poner la primera letra mayuscula
        apellido = request.form["apellido"].strip().capitalize()
        email = request.form["email"].strip().lower()#Borra los espacios extra y primera letra minuscula
        tipo = request.form["tipo"]

        # Validamos el DNI y el email
        # Si no son validos, retornamos un mensaje de error
        if not validarDNI(dni) or not validarMail(email):
            return "Datos invalidos, vuelva a intentarlo"
        

        pacientes = cargar_pacientes()
        # Verificamos si el paciente ya existe
        for paciente in pacientes:
            if paciente["dni"] == dni:
                return "El paciente ya existe"

        # Si no existe, lo agregamos
        pacientes.append({
            "dni": dni,
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "tipo": tipo
        })
        
        # Guardamos los datos en el .json
        guardar_pacientes(pacientes)
        return redirect(url_for("index"))
    
    # Si la solicitud es GET, mostramos el formulario
    return render_template("nuevo.html", obras_sociales = obras_sociales)

# Editamos paciente
@app.route("/editar/<dni>", methods=["GET", "POST"])
def editar(dni):
    try:
        pacientes = cargar_pacientes()
        paciente = next((p for p in pacientes if p["dni"] == dni), None)
        if not paciente:
            return "Paciente no encontrado"

        if request.method == "POST":
            paciente["dni"] = request.form["dni"]
            paciente["nombre"] = request.form["nombre"].strip().capitalize()
            paciente["apellido"] = request.form["apellido"].strip().capitalize()
            paciente["email"] = request.form["email"].strip().lower()
            paciente["tipo"] = request.form["tipo"]

            guardar_pacientes(pacientes)
            return redirect(url_for("index"))  # <-- Esto es lo que te lleva al index

        return render_template("editar.html", paciente=paciente, obras_sociales=obras_sociales, id=dni)
    except Exception as e:
        return f"Error al editar el paciente {e}"

#Borramos turno
@app.route("/eliminar/<dni>")
def eliminar(dni):
    try:
        pacientes = cargar_pacientes()
        pacientes = [p for p in pacientes if p["dni"] != dni]
        guardar_pacientes(pacientes)
        return redirect(url_for("index"))
        return redirect("/")
    except Exception as e:
        return f"Error al eliminar el paciente {e}"

@app.route("/intusuario")
def intusuario():
    return render_template("intusuario.html")

if __name__ == "__main__":
    app.run(debug = True)