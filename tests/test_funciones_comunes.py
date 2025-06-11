#para testear esto se escribe simplemente PYTEST en la terminal
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from funciones_comunes import validarDNI, validarMail, cargar_pacientes, guardar_pacientes #importación de las funciones que se prueban en el pytest que están en funciones_comunes.py

def test_email_valido():
    assert validarMail("pepito@gmail.com") == True #"camino feliz"

def test_email_invalido_sin_arroba():
    assert validarMail("pepitogmail.com") == False #sin arroba debe retornar falso

def test_email_invalido_sin_punto():
    assert validarMail("pepito@gmailcom") == False #sin punto debe retornar falso

def test_email_invalido_vacio(): #campo vacío no se debe permitir
    assert validarMail("") == False

def test_email_invalido_sin_nombre(): #tiene que haber texto antes del arroba
    assert validarMail("@gmail.com") == False

def test_email_invalido_sin_dominio(): #tiene que haber texto después del arroba
    assert validarMail("pepito@") == False

def test_email_invalido_con_espacios(): #no pueden haber espacios en el email
    assert validarMail("pepito @gmail.com") == False

def test_dni_valido():
    assert validarDNI("12345678") == True #"camino feliz", 8 digitos

def test_dni_invalido_con_letras():
    assert validarDNI("12A45678") == False #no puede haber un dni con letras

def test_dni_corto():
    assert validarDNI("1234") == False #el dni tiene que tener 8 digitos

def test_dni_largo_con_letras():
    assert validarDNI("123456789A") == False #no puede extenderse de 8 digitos ni tener letras

def test_dni_corto_con_letras():
    assert validarDNI("123A") == False #no puede ser más corto de 8 digitos ni tener letras

def test_dni_largo():
    assert validarDNI("123456789") == False #no tienen que extender se 8 digitos

def test_dni_vacio():
    assert validarDNI("") == False #tienen que haber contenido en el campo dni


def test_guardar_y_cargar_pacientes(tmp_path): #camino temporal, esto es para testear los guardados en el json, crear datos temporales para testear
    archivo = tmp_path / "pacientes.json" #camino temporal al json

    pacientes = [
        {"nombre": "Juan", "apellido": "Pérez", "dni": "12345678", "email": "juan@gmail.com"}
    ]
    guardar_pacientes(pacientes, str(archivo)) #
    leidos = cargar_pacientes(str(archivo))
    assert leidos == pacientes #se testea que el guardado y la lectura se el mismo dato

def test_cargar_pacientes_vacio(tmp_path):
    archivo = tmp_path / "pacientes.json"
    archivo.write_text("")

    pacientes = cargar_pacientes(str(archivo))
    assert pacientes == [] #se testea que se devuelva una lista vacia si el archivo está vacío

def test_cargar_pacientes_corrupto(tmp_path):
    archivo = tmp_path / "pacientes.json"
    archivo.write_text("esto no es un json") #se escribe un contenido no válido para el json que necesitamos para el sistema

    pacientes = cargar_pacientes(str(archivo)) #carga del archivo
    assert pacientes == [] #se vuelve una lista vacía, porque el archivo tiene contenido que no debe y está corrupto

def test_cargar_pacientes_no_existe(tmp_path):
    archivo = tmp_path / "pacientes.json"

    if archivo.exists():
        archivo.unlink() #acá se elimina el archivo (temporalmente solo para el test, obvio)
    pacientes = cargar_pacientes(str(archivo)) #se intenta carga un archivo que no exite
    assert pacientes == [] #se vuelve entonces una lista vacia

def test_guardar_caracteres_especiales(tmp_path): #por tíldes y Ñ
    archivo = tmp_path / "pacientes.json"

    pacientes = [
        {"nombre": "José", "apellido": "Muñoz", "dni": "33333333", "email": "jose@test.com"}
    ]
    guardar_pacientes(pacientes, str(archivo))
    cargados = cargar_pacientes(str(archivo))
    assert cargados == pacientes #se verifica que no haya habido problema en el guardado de datos con caracteres del español
