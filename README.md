# gestorTurnos

Creación de pagina web donde administrador podra ver todos los turnos de cada uno de los clientes, y subir nuevos manualmente.
Los clientes tambien podran ingresar en esta web y crear un usuario como clientes para poder agendar sus propios turnos medicos en base a su necesidad y disponibilidad. Cada usuario podra ver unicamente sus propios turnos, no el de los demas.

Primer vistazo de la pagina
Apartado para iniciar sesion o creacion de usuario. Dependiendo del usuario se redigira a dos apartados diferentes (Admin / cliente).
Al no tener usuario se puede registrar uno nuevo.

El siguiente vistazo seria poder ver la ventana de turnos creados (dependiendo del usuario). Los turnos podran ser editados o cancelados.

Por ultimo, el usuario podra generar un nuevo turno dependiendo de la disponibilidad.

Que tenemos hecho:

Al inicar el programa se te llevara hacia una pagina web dirigida con Flask donde se podra ver la lista de turnos y los diferentes botones para crear, editar y eliminar los turnos. Cada uno de estos se vera guardado en un archivo JSON.

Por otro lado, tambien tenemos el apartado para iniciar secion o registrar nuevo usuario creado. En este apartado contamos con 2 listas diferentes.
Una lista que guarda los datos los cuales se usar para iniciar sesion como administrador.
Y la segunda lista que se utiliza para leer los usuarion ya existentes o almacenar los nuevos.


Pasos a seguir

Unificacion de los diferentes programas que tenemos actualmente. Inicio de sesion y los turnos.
Desarrollar la interfaz de usuario donde a cada uno solo le aparezcan sus propios turnos y al admin los de todos.
Seccion para historial de turnos previos.


Proximas entregas

29/05


05/06


12/06
