function getCookie(name) { // usando protección CSRF (por defecto sí) para que no rechace server
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener("DOMContentLoaded", () => {

    /* FUNCIONES */
    function agregarPersona(container, plantilla, max) {
        cant_actual = container_persona.querySelectorAll(".persona").length;
        if (cant_actual < max) {
            const clon = plantilla.firstElementChild.cloneNode(true);
            clon.querySelectorAll("input").forEach(input => input.value = "");

            clon.querySelector(".eliminar-persona").addEventListener("click", () => clon.remove());

            container.appendChild(clon);
        } else {
            console.log("Llegaste al maximo de personas aceptadas");
        }
    }

    function completarReserva(container_persona) {
        const personas = [];
        const campos = container_persona.querySelectorAll(".persona");

        if (campos.length === 0) {
            alert("¡Debe agregar al menos una persona!");
            return;
        }

        for (let campo of campos) {
            const nombre = campo.querySelector("input[name='nombre']").value.trim();
            const edad = campo.querySelector("input[name='edad']").value.trim();
            const dni = campo.querySelector("input[name='dni']").value.trim();

            if (!nombre || !edad || !dni) {
                alert("¡Complete todos los campos de cada persona!");
                return;
            }

            personas.push({ nombre_completo: nombre, edad: edad, dni: dni });
        }

        // Obtenemos fechas y método de pago del formulario
        const fecha_inicio = document.querySelector("input[name='fecha_inicio']").value;
        const fecha_fin = document.querySelector("input[name='fecha_fin']").value;
        const metodo_pago = document.querySelector("select[name='metodo_pago']").value;

        if (!fecha_inicio || !fecha_fin || !metodo_pago) {
            alert("Complete todos los campos del formulario.");
            return;
        }

        // Construimos objeto para enviar
        const datosForm = new FormData();
        datosForm.append("csrfmiddlewaretoken", document.querySelector("input[name='csrfmiddlewaretoken']").value);
        datosForm.append("fecha_inicio", fecha_inicio);
        datosForm.append("fecha_fin", fecha_fin);
        datosForm.append("metodo_pago", metodo_pago);
        datosForm.append("datos_inquilinos", JSON.stringify(personas)); // JSON serializado

        // Enviamos el form manualmente
        fetch(window.location.href, {
            method: "POST",
            body: datosForm
        })
        .then(res => {
            if (res.redirected) {
                window.location.href = res.url;
            } else {
                return res.json().then(data => {
                    const errores = JSON.parse(data.error); // el backend manda los errores como string JSON
                    const mensajes = Object.values(errores)
                        .flat()
                        .map(err => err.message);
                    alert(mensajes.join("\n"));
                });
            }
        })
        .catch(err => console.error("Error al enviar reserva:", err));
    }

    /* MAIN */

    let datos_formulario = {
        fecha_inicio: null,
        fecha_fin: null,
        personas: [],
        metodo_pago: null
    };

    const agregar_persona = document.getElementById("agregar-persona");
    const completar_reserva = document.getElementById("completar-reserva");

    const max_inquilino = parseInt(document.getElementById("max-inquilino").innerText, 10);

    const plantilla = document.getElementById("formulario-persona-plantilla");
    const container_persona = document.getElementById("container-persona");

    agregar_persona.addEventListener("click", () => agregarPersona(container_persona, plantilla, max_inquilino));
    completar_reserva.addEventListener("click", () => completarReserva(container_persona));
});