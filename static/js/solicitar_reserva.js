function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener("DOMContentLoaded", () => {
    const container_widget = document.getElementById("container-widget");
    const inmuebleId = container_widget.getAttribute("data-inmueble-id");
    const cantPersonasMax = 1//parseInt(container_widget.getAttribute("data-cant-personas"));

    const agregar_persona = document.getElementById("agregar-persona");
    const continuar_reserva = document.getElementById("continuar-reserva");
    const container_persona = document.getElementById("container-persona");
    const plantilla = document.getElementById("formulario-persona-plantilla");

    let datos_formulario = {
        fecha_inicio: null,
        fecha_fin: null,
        personas: [],
        metodo_pago: null
    };

    function agregarPersona() {
        const actuales = container_persona.querySelectorAll(".persona").length;
        if (actuales >= cantPersonasMax) {
            alert(`Máximo permitido: ${cantPersonasMax} inquilinos.`);
            return;
        }

        const clon = plantilla.firstElementChild.cloneNode(true);
        clon.querySelectorAll("input").forEach(input => input.value = "");

        clon.querySelector(".eliminar-persona").addEventListener("click", () => {
            clon.remove();
        });

        container_persona.appendChild(clon);
    }

    function continuarReserva() {
        const personasDivs = container_persona.querySelectorAll(".persona");

        if (personasDivs.length === 0) {
            alert("¡Agregá al menos un inquilino!");
            return;
        }

        const personas = [];

        for (let div of personasDivs) {
            const nombre = div.querySelector("input[name='nombre']").value.trim();
            const edad = div.querySelector("input[name='edad']").value.trim();
            const dni = div.querySelector("input[name='dni']").value.trim();

            if (!nombre || !edad || !dni) {
                alert("Completá todos los campos de cada inquilino.");
                return;
            }

            personas.push({ nombre_completo: nombre, edad, dni });
        }

        datos_formulario.personas = personas;
        datos_formulario.metodo_pago = document.getElementById("metodo_pago").value;
        datos_formulario.fecha_inicio = document.querySelector("input[name='fecha_inicio']").value;
        datos_formulario.fecha_fin = document.querySelector("input[name='fecha_fin']").value;

        if (!datos_formulario.fecha_inicio || !datos_formulario.fecha_fin) {
            alert("Seleccioná fecha de inicio y fin.");
            return;
        }

        fetch(`/reserva/crear/?inmueble_id=${inmuebleId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie('csrftoken')
            },
            body: JSON.stringify(datos_formulario)
        })
        .then(res => res.json())
        .then(data => {
            alert("Reserva enviada correctamente ✅");
            location.reload();
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Error al guardar la reserva ❌");
        });
    }

    agregar_persona.addEventListener("click", () =>agregarPersona());
    continuar_reserva.addEventListener("click", continuarReserva);
});
