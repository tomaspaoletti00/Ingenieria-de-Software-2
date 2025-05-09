document.addEventListener("DOMContentLoaded", () => {
    const botones = document.getElementsByClassName("form-button");
    const container = document.getElementById("container-form");

    Array.from(botones).forEach(element => {
        element.addEventListener("click", () => {
            const tipo = element.dataset.tipo
            fetch(`/inmuebles/formulario/?tipo=${tipo}`)
                .then(response => response.text())
                .then(data => {
                    container.innerHTML = data;
                })
                .catch(error => console.error("Error al cargar el formulario:", error));
        });
    });
});