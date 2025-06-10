document.addEventListener("DOMContentLoaded", () => {
    const agregar_persona = document.getElementById("agregar-persona");
    const container_persona = document.getElementById("container-persona");
    const plantilla = document.getElementById("formulario-persona-plantilla");
    const input_oculto = document.getElementById("datos-inquilinos-hidden");
    const max = parseInt(container_persona.dataset.max, 10);

    agregar_persona.addEventListener("click", () => {
        if (container_persona.querySelectorAll(".persona").length >= max) {
            Swal.fire({
                icon: 'info',
                title: 'Máximo alcanzado',
                text: 'La cantidad de inquilinos ya es la máxima.',
                animation: false,
            });
            return;
        }

        const clon = plantilla.firstElementChild.cloneNode(true);
        clon.querySelector(".eliminar-persona").addEventListener("click", () => clon.remove());
        container_persona.appendChild(clon);
    });

    // Validación y armado del JSON antes del submit
    document.getElementById("formulario-reserva").addEventListener("submit", (e) => {
        const personas = [];
        let campos_incompletos = false;

        container_persona.querySelectorAll(".persona").forEach(div => {
            const nombre = div.querySelector("input[name='nombre']").value.trim();
            const edad = div.querySelector("input[name='edad']").value.trim();
            const dni = div.querySelector("input[name='dni']").value.trim();

            const nombreValido = /^[A-Za-zÁÉÍÓÚÑáéíóúñ\s]+$/.test(nombre);
            const dniValido = /^\d+$/.test(dni);
            const edadValida = /^\d+$/.test(edad) && parseInt(edad, 10) >= 0;

            if (!nombre || !edad || !dni || !nombreValido || !dniValido || !edadValida) {
                campos_incompletos = true;
            } else {
                personas.push({ nombre_completo: nombre, edad: edad, dni: dni });
            }
        });

        if (personas.length === 0 || campos_incompletos) {
            e.preventDefault();
            Swal.fire({
                icon: 'error',
                title: 'Campos inválidos',
                text: 'Completá todos los campos con datos válidos (nombre solo letras, DNI solo números).',
                animation: false,
            });
        } else {
            input_oculto.value = JSON.stringify(personas);
        }
    });
});
