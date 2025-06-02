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

    const metodo_pago = document.querySelector("select[name='metodo_pago']").value;
    if (!metodo_pago) {
        alert("Seleccione un método de pago.");
        return;
    }

    // 🔍 Detectar tipo de inmueble
    const tipoInmueble = document.getElementById("tipo-inmueble")?.value;

    let fecha_inicio_iso, fecha_fin_iso;
    if (tipoInmueble === "Cochera") {
        const dia = document.querySelector("input[name='dia']").value;
        const hora_inicio = document.querySelector("select[name='hora_inicio']").value;
        const horas = parseInt(document.querySelector("input[name='horas']").value, 10);

        if (!dia || !hora_inicio || isNaN(horas)) {
            alert("Debe completar el día, hora de inicio y cantidad de horas.");
            return;
        }

        const fecha_inicio = new Date(`${dia}T${hora_inicio}:00`);
        const fecha_fin = new Date(fecha_inicio.getTime() + horas * 60 * 60 * 1000);

        fecha_inicio_iso = fecha_inicio.toISOString().slice(0, 16);
        fecha_fin_iso = fecha_fin.toISOString().slice(0, 16);
    } else {
        // Departamento (reserva por día)
        fecha_inicio_iso = document.querySelector("input[name='fecha_inicio']").value;
        fecha_fin_iso = document.querySelector("input[name='fecha_fin']").value;

        if (!fecha_inicio_iso || !fecha_fin_iso) {
            alert("Debe completar fecha de inicio y fin.");
            return;
        }
    }

    const datosForm = new FormData();
    console.log("hola");
    console.log("Fecha fin ISO:", fecha_fin_iso);
    datosForm.append("csrfmiddlewaretoken", document.querySelector("input[name='csrfmiddlewaretoken']").value);
    datosForm.append("fecha_inicio", fecha_inicio_iso);
    datosForm.append("fecha_fin", fecha_fin_iso);
    datosForm.append("metodo_pago", metodo_pago);
    datosForm.append("datos_inquilinos", JSON.stringify(personas));
    console.log("Enviando datos:");
    console.log("fecha_inicio", fecha_inicio_iso);
    console.log("fecha_fin", fecha_fin_iso);
    console.log("metodo_pago", metodo_pago);
    console.log("personas", personas);
    
    fetch(window.location.href, {
        method: "POST",
        body: datosForm
    })
    .then(res => {
        if (res.redirected) {
            window.location.href = res.url;
        } else {
            return res.json().then(data => {
                const errores = JSON.parse(data.error);
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