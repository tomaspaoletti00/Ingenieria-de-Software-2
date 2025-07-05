document.addEventListener("DOMContentLoaded", () => {
    const agregarPersona = document.getElementById("agregar-persona");
    const containerPersona = document.getElementById("container-persona");
    const plantilla = document.getElementById("formulario-persona-plantilla");
    const inputOculto = document.getElementById("datos-inquilinos-hidden");
    const max = parseInt(containerPersona.dataset.max, 10);

    if (agregarPersona) {
        agregarPersona.addEventListener("click", () => {
            if (containerPersona.querySelectorAll(".persona").length >= max) {
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
            containerPersona.appendChild(clon);
        });
    }

    // Validación y armado del JSON antes del submit
    document.getElementById("formulario-reserva").addEventListener("submit", (e) => {
        const personas = [];
        const campos = containerPersona.querySelectorAll(".persona");

        const soloLetras = /^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$/;
        const soloNumeros = /^[0-9]+$/;

        let camposIncompletos = false;

        for (const div of campos) {
            const nombre = div.querySelector("input[name='nombre']").value.trim();
            const edad = div.querySelector("input[name='edad']").value.trim();
            const dni = div.querySelector("input[name='dni']").value.trim();

            const nombreValido = soloLetras.test(nombre);
            const dniValido = soloNumeros.test(dni);
            const edadValida = soloNumeros.test(edad) && parseInt(edad, 10) >= 0;

            if (!nombre || !edad || !dni || !nombreValido || !dniValido || !edadValida) {
                camposIncompletos = true;
            } else {
                personas.push({ nombre_completo: nombre, edad: edad, dni: dni });
            }
        }

        if (personas.length === 0 || camposIncompletos) {
            e.preventDefault();
            Swal.fire({
                icon: 'error',
                title: 'Campos inválidos',
                text: 'Completá todos los campos con datos válidos (nombre solo letras, DNI solo números).',
                animation: false,
            });
            return;
        }

        inputOculto.value = JSON.stringify(personas);
    });
});
