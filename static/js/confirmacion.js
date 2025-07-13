document.addEventListener("DOMContentLoaded", function () {
    const botonesEliminar = document.querySelectorAll(".btn-eliminar"); //se seleccionan todos los botones que tengan la clase btn-eliminar, en este caso, eliminar pacientes

    botonesEliminar.forEach(function (boton) {
        boton.addEventListener("click", function (e) { //se escucha el evento click en el boton de eliminar paciente
            const confirmar = confirm("¿Estás seguro de que querés eliminar este paciente?"); //se muestra un mensaje de confirmación
            if (!confirmar) {
                e.preventDefault(); 
            }
        });
    });

    const botonesEliminarTurno = document.querySelectorAll(".btn-eliminar-turno"); //se seleccionan todos los botones que tengan la clase btn-eliminar-turno, en este caso, cancelar turno
    botonesEliminarTurno.forEach(function (boton) {
        boton.addEventListener("click", function (e) { //se escucha el evento click en el boton de cancelar turno
            const confirmar = confirm("¿Estás seguro de que querés cancelar tu turno?"); //se muestra un mensaje de confirmación
            if (!confirmar) {
                e.preventDefault(); //
            }
        });
    });
});
