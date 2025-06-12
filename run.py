from flask import Flask
from administrador.app import pacientes_bp
from registro.admin import admin_bp #
from datetime import timedelta #para que la sesión pueda permanecer iniciada



app = Flask(__name__) #creación de la aplicación flask
app.secret_key = 'clave' #clave secreta para la aplicación, se usa para firmar cookies (que por ejemplo permite que la sesión pueda permanecer iniciada) y proteger la sesión del usuario
app.permanent_session_lifetime = timedelta(days=7) #la sesión permanecerá iniciada por 7 días

app.register_blueprint(admin_bp) #registramos el blueprint de admin.py para que pueda ser usado en la aplicación, ayudando a organizar el código y las rutas
app.register_blueprint(pacientes_bp) #registramos el blueprint de pacientes.py para que pueda ser usado en la aplicación, ayudando a organizar el código y las rutas

if __name__ == "__main__": 
    app.run(debug=True) #para que no haya que volver a escribir en la terminal cada vez que se quiera ejecutar el programa