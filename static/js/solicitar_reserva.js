document.addEventListener("DOMContentLoaded", () => {
    const reserva_normal = document.getElementById("reserva-normal");
    const container_widget = document.getElementById("container-widget")

    reserva_normal.addEventListener("click", () => {
        fetch("/reserva/prueba/normal")
            .then(response => response.text())
            .then(data => container_widget.innerHTML = data)
            .catch(error => console.error("Error al cargar el formulario:", error));
    });

    const agregar_persona = document.getElementById("agregar-persona");
    const eliminar_persona = document.getElementById("eliminar-persona");
    const continuar_reserva = document.getElementById("continuar-reserva");

    const container_persona = document.getElementById("container-persona");

    agregar_persona.addEventListener("click", () => {
        const clon = document.getElementsById("persona").cloneNode(true);
        container_persona.appendChild(clon);
    })
});