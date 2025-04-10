
paciente = []

def procesoval(a):
    if a < 10000000000 or a > 99999999999:
        print("Su dni debe tener exactamente 11 digitos: ")
        return False
    return True

def mailval(b):
    if "@" not in b:
        print("Su mail no es valido, porfavor ingreselo nuevamente")
        return False
    return True


proceso = int(input("Ingrese un dni valido o -1 para terminar: "))
while proceso != -1:
    while not procesoval(proceso):
        proceso = int(input("Ingrese un dni con 11 digitos o -1 para terminar: "))

    if proceso != -1:
        paciente.append(proceso)
        nombyapel = input("Ingrese el nombre y apellido del paciente: ")
        paciente.append(nombyapel)
        mail = input("Ingrese el mail del paciente: ")

    while not mailval(mail):
        mail = input("Ingrese un mail valido porfavor: ")

    paciente.append(mail)
    part = int(input("Ingrese 1 si es un particular o 2 si posee una obra social: "))
    while part > 2 or part < 1:
        part = int(input("Ingrese un numero entre 1 y 2, 1 si es un particular o 2 si posee obra social: "))
    else:
        paciente.append(part)

    proceso = int(input("Ingrese otro DNI o -1 para terminar: "))
else:
    print(paciente)


