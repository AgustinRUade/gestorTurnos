from flask import Flask
from administrador.admin import admin_bp
from turnos.turnos import turnos_bp

app = Flask(__name__)
app.secret_key = "clave_supersecreta"

app.register_blueprint(admin_bp)
app.register_blueprint(turnos_bp, url_prefix="/turnos")

if __name__ == "__main__":
    app.run(debug=True)