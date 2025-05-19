document.addEventListener("DOMContentLoaded", () => {
    /* FUNCIONES */

    function agregarPersona(container, plantilla) {
        const clon = plantilla.firstElementChild.cloneNode(true);
        clon.querySelectorAll("input").forEach(input => input.value = "");

        clon.querySelector(".eliminar-persona").addEventListener("click", () => clon.remove());

        container.appendChild(clon);
    }

    function continuarReserva(container_persona) {
        if (container_persona.querySelectorAll(".persona").length === 0) {
            console.log("¡Mínimo un inquilino!");
            return;
        }

        const personas = [];
        const campos = container_persona.querySelectorAll(".persona");

        for (let campo of campos) {
            const nombre = campo.querySelector("input[name='nombre']").value.trim();
            const edad = campo.querySelector("input[name='edad']").value.trim();
            const dni = campo.querySelector("input[name='dni']").value.trim();

            if (!nombre || !edad || !dni) {
                console.log("¡Llenar todos los campos!");
                return;
            }

            personas.push({ nombre_completo: nombre, edad: edad, dni: dni });
        }

        datos_formulario.personas = personas;
        datos_formulario.fecha_inicio = document.querySelector("input[name='fecha_inicio']").value;
        datos_formulario.fecha_fin = document.querySelector("input[name='fecha_fin']").value;
        console.log(datos_formulario);
    }

    function inicializarFormularioReserva(data) {
        container_widget.innerHTML = data;

        const agregar_persona = document.getElementById("agregar-persona");
        const continuar_reserva = document.getElementById("continuar-reserva");
        const container_persona = document.getElementById("container-persona");
        const plantilla = document.getElementById("formulario-persona-plantilla");

        agregar_persona.addEventListener("click", () => agregarPersona(container_persona, plantilla));
        continuar_reserva.addEventListener("click", () => continuarReserva(container_persona));
    }

    /* MAIN */

    const reserva_normal = document.getElementById("reserva-normal");
    const container_widget = document.getElementById("container-widget");

    let datos_formulario = {
        fecha_inicio: null,
        fecha_fin: null,
        personas: [],
        metodo_pago: null
    };

    reserva_normal.addEventListener("click", () => {
        fetch("/reserva/prueba/normal")
            .then(response => response.text())
            .then(data => inicializarFormularioReserva(data))
            .catch(error => console.error("Error al cargar el formulario:", error));
    });
});