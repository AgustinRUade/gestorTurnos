from flask import Flask
from administrador.app import pacientes_bp
from registro.admin import admin_bp

app = Flask(__name__)
app.secret_key = 'clave'

app.register_blueprint(admin_bp)
app.register_blueprint(pacientes_bp)


if __name__ == "__main__":
    app.run(debug=True)