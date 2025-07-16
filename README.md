# 🏠 Alquiler Express

**Alquiler Express** es una aplicación web desarrollada como parte de la materia **Ingeniería de Software 2 (UNLP)**. El sistema permite gestionar propiedades en alquiler, facilitando el trabajo de administradores, empleados y usuarios.

---

## 🚀 Funcionalidades principales

- Registro e inicio de sesión con roles diferenciados (Administrador / Empleado / Cliente)
- Gestión de inmuebles (crear, editar, eliminar)
- Visualización de propiedades disponibles
- Reserva de inmuebles por parte de los clientes
- Gestión de reservas pendientes por parte de empleados
- Filtros dinámicos en la búsqueda de inmuebles
- Cálculo de precios según duración de la estadía
- Panel de administración con acceso restringido

---

## ⚙️ Tecnologías utilizadas

- Python 3 + Django
- HTML, CSS, JavaScript
- SQLite (desarrollo) / PostgreSQL (producción)
- Bootstrap (opcional)
- Flatpickr (para selección de fechas)

---

## 🧪 Pruebas

El sistema incluye validaciones tanto del lado del servidor como del cliente.  
Se aplicaron estrategias de prueba **caja negra** (validaciones de entradas/salidas, flujo de uso) y **caja blanca** (verificación de lógica y condiciones) sobre las funcionalidades críticas del sistema.

---

## 📦 Instalación

```bash
git clone https://github.com/tomaspaoletti00/Ingenieria-de-Software-2.git
cd alquiler-express
python -m venv venv
source venv/bin/activate  # o .\venv\Scripts\activate en Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 👨‍💻 Equipo de desarrollo

Tomás Paoletti

Valentino Ongaro

Lautaro Acuña

Isidro Iveli
