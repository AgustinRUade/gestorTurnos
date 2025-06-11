from datetime import datetime #para poder registrar la fecha y hora de cuando se registra un suceso en el archivo .log
import re #para poder validar el formato del email ingresado por el usuario
import json
import os 

PACIENTES_JSON = "pacientes.json"  #Archivo donde se guardan los pacientes

def registrar_log(texto):
    fecha_hora = datetime.now().strftime("%d-%m-%Y %H:%M:%S") #para que en el archivo .log se registre día(%d), mes(%m), año(%Y), hora(%H), minuto(%M) y segundo(%S) de cuando sucedió lo que se registra
    #EXPLICACIÓN: se usa strftime para formatear la fecha y hora de acuerdo a lo que se necesita, en este caso, día, mes, año, hora, minuto y segundo
    try: #se usa try-except para manejar errores al escribir en el archivo, si hay un error, se imprime un mensaje de error en la consola
        archivo = open("archivo.log", "a", encoding="utf-8") #EXPLICACIÓN: se abre el archivo en modo append ("a") donde no se borra lo que ya está escrito, sino que se agregue al final, no es una reescritura como si es "w". Se usa encoding="utf-8" para que se puedan escribir caracteres especiales
        archivo.write(f"[{fecha_hora}] {texto}\n") #se escribe en el archivo (.write)
        archivo.close() #EXPLICACIÓN: se cierra el archivo para que no quede abierto y se pueda seguir escribiendo en él
    except Exception as e: #la excepción con alias "e" captura cualquier error que ocurra al intentar escribir en el archivo
        print("Error escribiendo en el log:", e) #print para mostrar un mensaje de error en la consola, obvio, si es que hubo error

def registrar_error(e): 
    fecha_hora = datetime.now().strftime("%d-%m-%Y %H:%M:%S") #lo mismo que en la función registrar_log, pero en esta función el objetivo es registrar errores
    tipo = type(e).__name__ #se usa type(e).__name__ para obtener el nombre de la clase de la excepción, por ejemplo, si es un ValueError, TypeError etc etc...
    mensaje = str(e) #y acá se convierte la excepción en un string para poder escribirla en el archivo .log
    try:
        archivo = open("archivo.log", "a", encoding="utf-8") #igual que en la función registrar_log, se abre el archivo en modo append ("a") para agregar al final del archivo
        archivo.write(f"[{fecha_hora}] [ERROR] Tipo: {tipo} - Mensaje: {mensaje}\n") #se escribe en el archivo el error con la fecha y hora, el tipo de error y el mensaje del error
        archivo.close() #igual que la función de registrar log, se cierra el archivo, porque sino se rompe, y no se puede seguir escribiendo en él
    except Exception as e: #otra vez, error de escritura en el archivo, se captura la excepción con alias "e"
        print("No se pudo registrar el error:", e) #y se imprime un mensaje de error en la consola

def validarDNI(dni): #validar el formato del dni
    return dni.isdigit() and len(dni) == 8 #para verificar que el dni ingresado sea un número (isdigit) y que tenga 8 dígitos (len(dni) == 8), si las dos cosas se cumplen, retorna true, sino retorna false

def validarMail(email): #validar el formato del email
    return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email) is not None
    #EXPLICACIÓN: se verifica que el formato del email ingresado matchee con el formato definido (re.match). Ahora, la expresión, antes del arroba, admite letras minusculas y mayusculas de la A a la Z, números del 0 al 9, guiones bajos, puntos, guiones y signos de más. Después del arroba, admite letras minusculas y mayusculas de la A a la Z, números del 0 al 9 y guiones. Luego, debe haber un punto seguido de letras minusculas y mayusculas de la A a la Z, números del 0 al 9 y guiones.
    #en el pytest quizás se muestra mejor, pero al escribir el formato de esta manera no se guarda un email con espacios, el usuario está obligado a escribir texto antes del arroba, después del arroba, a poner un punto y a poner texto después de este.


#Función para cargar la lista de pacientes desde el archivo JSON.          
def cargar_pacientes(ruta="pacientes.json"): #esta y la función de abajo SE REPETÍAN en los dos .py que tenemos, ENTONCES puse estas dos funciones acá para que no se repitan y se puedan usar en ambos archivos por imports (vean las primeras líneas de los archivos .py, dice from funciones_comunes import etc etc), supongo que hace al código más limpio, no se redunda por demás, de cualquier manera se puede reveer                             
    if not os.path.exists(ruta): #si el archivo no existe o está vacio, retorna una lista vacía
        return [] 
    try: #
        with open(ruta, "r", encoding="utf-8") as f: #abrimos el archivo en modo lectura ("r") y con codificación utf-8 para que se puedan leer caracteres especiales
            #se usa "with" para abrir el archivo, esto asegura que el archivo se cierre automáticamente al finalizar el bloque, incluso si ocurre un error. NO LO VIMOS EN CLASE, reveer si se quiere mantener esto así, es de versiones anteriores del desarrollo.
            return json.load(f) #
    except (FileNotFoundError, json.JSONDecodeError) as e: #
            registrar_error(e) #si el archivo está corrupto, registra el error en el archivo .log
                               #EXPLICO: se llama a la función registrar_error con el error capturado como parametro(e), para que se registre en el ERROR en el archivo .log a través de la función destinada a escribir errores
            return [] #esto asumo que es redundante con el if de arriba, repensarlo

# Función para guardar la lista de pacientes en el archivo JSON.
# Sobrescribe el archivo con la nueva lista de pacientes.
def guardar_pacientes(pacientes, ruta="pacientes.json"):                                    #se repite misma funcion en admin.py
    try:
        with open(ruta, "w", encoding="utf-8") as f: 
            json.dump(pacientes, f, ensure_ascii=False, indent=4)
    except Exception as e:
        registrar_error(e) #si hubo un error al guardar los pacientes, registra el error en el archivo .log. 
