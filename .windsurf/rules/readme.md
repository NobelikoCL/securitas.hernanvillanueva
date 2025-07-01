---
trigger: always_on
---

Reglas Generales del ERP de Seguridad CORE
1. Propósito y Enfoque del ERP
El ERP de Seguridad CORE es un Sistema de Planificación de Recursos Empresariales diseñado para centralizar y optimizar la gestión de personal de seguridad, flota de vehículos y operaciones diarias para las instalaciones o clientes de una empresa de seguridad.

Su objetivo principal es 100% operacional: garantizar la cobertura de servicios, anticipar problemas y automatizar la comunicación. Busca aliviar la carga del Administrador de Contrato, eliminando la necesidad de herramientas fragmentadas (como planillas Excel o grupos de WhatsApp) al convertirse en la única fuente de verdad para la planificación. El cumplimiento legal es una restricción fundamental que debe ser considerada en la funcionalidad.

El usuario objetivo incluye a Administradores de Contrato, Jefes de Operaciones y Supervisores.

2. Decisiones de Arquitectura y Tecnologías
Sin Autenticación Inicial
El proyecto NO incluye un sistema de autenticación (login/logout) en su desarrollo inicial. Esta es una decisión de diseño intencional para simplificar y acelerar la fase inicial.

Consideraciones para Futura Implementación de Autenticación:
Si la autenticación se requiere en el futuro, se deberán seguir estos pasos:

Configurar el sistema de autenticación de Django.

Agregar las URLs de autenticación en urls.py.

Crear las plantillas de login/logout.

Agregar LoginRequiredMixin a las vistas que lo requieran.

Configurar las variables relacionadas en settings.py.

Tecnologías Clave
Backend: Django 5.2.3 (Python)

Base de Datos: SQLite (para desarrollo), PostgreSQL (para producción). El uso del ORM de Django facilita la migración a bases de datos más robustas.

Frontend:

Bootstrap 5

FullCalendar.js (para el calendario de turnos)

jQuery

Font Awesome

Chart.js (para gráficos de reportes)

Generación de Documentos:

ReportLab

WeasyPrint

Automatización Externa:

El ERP expondrá información vía API REST o Webhooks para integrarse con herramientas como N8N, que actuará como el "brazo ejecutor" para automatizar notificaciones y flujos de trabajo.

3. Estructura del Proyecto
El proyecto seguirá las mejores prácticas de Django para modularidad y escalabilidad.

core/
├── core/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py           # Configuraciones globales del proyecto.
│   ├── urls.py               # Enrutador principal que delegará las URLs a la app 'erp'.
│   └── wsgi.py
├── erp/                      # Contendrá toda la lógica de negocio: modelos, vistas, plantillas y URLs.
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py             # Definición de la base de datos y modelos interconectados.
│   ├── tests.py
│   ├── views.py
│   ├── urls.py
│   ├── utils.py
│   └── templates/
│       └── erp/
│           ├── base.html
│           ├── dashboard.html
│           ├── calendar.html
│           ├── cliente_list.html
│           ├── cliente_detail.html
│           ├── instalacion/
│           │   └── ... (vistas de CRUD)
│           ├── personal/
│           │   └── ...
│           └── ... (resto de carpetas por módulo)
└── manage.py
4. Modelos de Datos (erp/models.py)
Los modelos definen la estructura de la base de datos y están interconectados para mantener la integridad de los datos.

Cliente: Información de las empresas clientes.

Instalacion: Detalles de los puestos o instalaciones específicas donde se brindan servicios, incluyendo cliente asociado y datos de contacto.

Cargo: Cargos laborales del personal de seguridad.

Personal: Información detallada de los empleados, incluyendo datos personales, contacto, cargo, estado de actividad y la instalación asignada. Incluye un campo usuario para futura integración con el sistema de autenticación de Django si aplica.

TipoVehiculo: Categorías de vehículos.

Vehiculo: Detalles de la flota vehicular, incluyendo patente, marca, modelo, tipo y estado de servicio.

Turno: Asignaciones de personal a instalaciones en fechas y horarios específicos, con cálculo automático de horas trabajadas.

TipoIncidencia: Categorías predefinidas de incidentes.

Incidencia: Registro de eventos e incidentes, detallando título, instalación, tipo, fechas, descripción, personal involucrado y estado.

5. Funcionalidades Implementadas
5.1. Dashboard (Página de Inicio - /home)
Será la "Torre de Control" principal, ofreciendo una interfaz limpia con:

Resumen Rápido: Estadísticas clave (personal activo, vehículos en servicio, incidencias abiertas, personal en turno).

Accesos Directos: Botones para operaciones comunes (crear incidencia, asignar turno, añadir personal).

Menú de Navegación Principal: Acceso a todos los módulos.

Menú de Configuración del Sistema: Desplegable para datos maestros.

5.2. Módulo: Gestión de Instalaciones
CRUD Completo para Clientes e Instalaciones.

La vista de detalle de una instalación mostrará: información general, listado de personal y vehículos asignados, y el historial de incidencias.

5.3. Módulo: Gestión de Personal
CRUD Completo para la entidad Personal.

Filtros de búsqueda por nombre, RUT, cargo o instalación.

La vista de detalle de un miembro del personal mostrará: información personal y de contacto, historial de turnos trabajados e incidencias en las que ha estado involucrado.

Mejora Futura: Posibilidad de añadir un sub-módulo para gestionar documentos (contrato, certificados OS10, etc.) mediante FileField.

5.4. Módulo: Gestión de Flota
CRUD Completo para la entidad Vehiculo.

Filtros por patente, tipo o instalación.

Mejora Futura: Añadir un sub-módulo de Mantenimiento para registrar fechas de revisiones, cambios de aceite, etc.

5.5. Módulo: Planner de Turnos (Corazón Operativo)
Este es el módulo más complejo y visual:

Interfaz de Calendario: Vista semanal o mensual utilizando FullCalendar.js. Las filas representan las instalaciones y las columnas los días, permitiendo asignar personal a turnos.

Generación Automática: Posibilidad de rellenar el calendario automáticamente con guardias que corresponden a cada ciclo.

Visualización por Colores:

Verde: Turno cubierto correctamente.

Rojo: Déficit de personal (dotación requerida no cumplida).

Amarillo: Cubierto, pero con un guardia que no cumple un requisito "deseable".

Naranja: Turno cubierto con un reemplazo de última hora.

Gris: Puesto no requiere cobertura.

Funcionalidad Inteligente para Reemplazos: Al detectar un déficit, el sistema mostrará una lista filtrada y priorizada de candidatos ideales basada en: disponibilidad, cumplimiento de habilidades y requisitos especiales obligatorios, conflictos (turnos ya asignados o excedencia de horas legales), proximidad y costo (opcional).

Funcionalidad: Crear, modificar y eliminar turnos, con validaciones para evitar superposición. Vista de dotación diaria.

5.6. Módulo: Gestión de Incidencias
CRUD Completo para la entidad Incidencia.

Formulario de creación intuitivo.

Sistema de notificaciones (opcional, por email).

Listado principal con filtros por estado, instalación o fecha.

Mejora Futura: Permitir adjuntar archivos (fotos, reportes en PDF) al modelo Incidencia.

5.7. Módulo: Estadísticas y Reportes (Próxima Mejora)
Generación de reportes visuales y exportables (PDF/Excel) utilizando librerías como Chart.js, ReportLab o WeasyPrint.

Ejemplos de reportes: Horas por Personal, Incidencias (por tipo/instalación), Asistencia, Kilometraje/Costo de Flota.

5.8. Módulo: Configuración del Sistema
Esta sección es para datos maestros que rara vez cambian, gestionables por un administrador:

CRUD para Cargo, TipoVehiculo, TipoIncidencia.

Gestión de Usuarios: Administración de usuarios del sistema y sus permisos, definiendo el acceso por módulo y roles (Administradores, Supervisores).

6. Proactividad y Automatización (Integración con N8N)
El ERP debe actuar como una "Torre de Control" operativa, pensando y avisando proactivamente mediante la integración con N8N (o herramientas similares) vía API REST o Webhooks.

Alertas Clave:
Déficit Futuro de Dotación: Escaneo diario del planner para detectar y alertar sobre faltantes de personal en los próximos días.

Vencimiento de Credencial Crítica: Escaneo diario de habilidades de empleados para alertar sobre vencimientos próximos de credenciales obligatorias (ej. OS10).

Workflows Esenciales con N8N:
Publicación de Planner Semanal: Envío automático del planner a los guardias vía WhatsApp, SMS o Email al ser publicado en el ERP.

Alerta de Incidencia Inmediata a Supervisores: Notificación automática a canales de comunicación (Slack, Telegram, WhatsApp) cuando se detecta un déficit o vencimiento crítico.

Búsqueda de Reemplazo Voluntario (Avanzado): Envío de un broadcast a candidatos ideales para cubrir turnos vacantes.

Recordatorio de Turno Diario: Envío de recordatorios individuales a los guardias con sus turnos para el día siguiente.

7. Instalación y Uso
Instalación:
Crear un entorno virtual: python -m venv venv

Activar el entorno virtual: .\venv\Scripts\activate

Instalar dependencias: pip install -r requirements.txt

Aplicar migraciones: python manage.py makemigrations y python manage.py migrate

Crear superusuario: python manage.py createsuperuser

Ejecutar el servidor: python manage.py runserver

Uso:
Acceder al sistema: http://localhost:8000/

Navegar entre los módulos usando el menú superior.

Utilizar el dashboard para estadísticas rápidas.

Usar el calendario para gestionar turnos.

Administrar personal, instalaciones y flota.

Registrar y gestionar incidencias.

8. Seguridad y Escalabilidad
Seguridad: Basada en el sistema de autenticación y permisos de Django (una vez implementado). Definición de roles (Administradores, Supervisores) con control de acceso por módulo, validación de datos en formularios y protección CSRF.

Escalabilidad: Uso del ORM de Django, posibilidad de migrar a PostgreSQL para producción, arquitectura modular y diseño responsive.

Backup: Se recomienda implementar una estrategia robusta de respaldo de la base de datos en producción.