document.addEventListener("DOMContentLoaded", () => {
    const agregar_persona = document.getElementById("agregar-persona");
    const container_persona = document.getElementById("container-persona");
    const plantilla = document.getElementById("formulario-persona-plantilla");
    const input_oculto = document.getElementById("datos-inquilinos-hidden");
    const max = parseInt(container_persona.dataset.max, 10);

    agregar_persona.addEventListener("click", () => {
        if (container_persona.querySelectorAll(".persona").length >= max) {
            Swal.fire({
                icon: 'info', // success, warning, info, question
                title: 'Maximo alcanzado',
                text: 'La cantidad de inquilinos ya es la maxima.',
                animation: false,
            });
            return;
        }

        const clon = plantilla.firstElementChild.cloneNode(true);
        clon.querySelector(".eliminar-persona").addEventListener("click", () => clon.remove());
        container_persona.appendChild(clon);
    });

    // Antes del submit, construir JSON de personas
    document.getElementById("formulario-reserva").addEventListener("submit", (e) => {
        const personas = [];
        const campos = container_persona.querySelectorAll(".persona");

        const soloLetras = /^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$/;
        const soloNumeros = /^[0-9]+$/;

        for (const div of campos) {
            const nombre = div.querySelector("input[name='nombre']").value.trim();
            const edad = div.querySelector("input[name='edad']").value.trim();
            const dni = div.querySelector("input[name='dni']").value.trim();

            if (
                !nombre ||
                !edad ||
                !dni ||
                isNaN(edad) ||
                parseInt(edad, 10) < 0 ||
                !soloLetras.test(nombre) ||
                !soloNumeros.test(dni)
            ) {
                e.preventDefault();
                Swal.fire({
                    icon: 'error',
                    title: 'Campos inválidos',
                    text: 'Todos los campos deben estar completos y ser válidos.',
                    animation: false,
                });
                return;  // ⚠️ muy importante, evitamos seguir el flujo
            }

            personas.push({ nombre_completo: nombre, edad: edad, dni: dni });
        }

        if (personas.length === 0) {
            e.preventDefault();
            Swal.fire({
                icon: 'error',
                title: 'Faltan inquilinos',
                text: 'Debe agregar al menos un inquilino válido.',
                animation: false,
            });
            return;
        }

        input_oculto.value = JSON.stringify(personas);
    });
});