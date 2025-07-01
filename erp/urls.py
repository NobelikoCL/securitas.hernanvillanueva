from django.urls import path
from . import views
from . import views_gestores

app_name = 'erp'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('calendario/', views.CalendarView.as_view(), name='calendar'),

    # Gestión Unificada de Clientes e Instalaciones
    path('gestion-clientes/', views.GestionClientesView.as_view(), name='gestion_clientes'),

    # Clientes (mantener compatibilidad)
    path('clientes/', views.ClienteListView.as_view(), name='cliente_list'),
    path('clientes/nuevo/', views.ClienteCreateView.as_view(), name='cliente_create'),
    path('clientes/<int:pk>/', views.ClienteDetailView.as_view(), name='cliente_detail'),
    path('clientes/<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='cliente_update'),
    path('clientes/<int:pk>/eliminar/', views.ClienteDeleteView.as_view(), name='cliente_delete'),

    # Instalaciones (mantener compatibilidad)
    path('instalaciones/', views.InstalacionListView.as_view(), name='instalacion_list'),
    path('instalaciones/nueva/', views.InstalacionCreateView.as_view(), name='instalacion_create'),
    path('instalaciones/<int:pk>/', views.InstalacionDetailView.as_view(), name='instalacion_detail'),
    path('instalaciones/<int:pk>/editar/', views.InstalacionUpdateView.as_view(), name='instalacion_update'),
    path('instalaciones/<int:pk>/eliminar/', views.InstalacionDeleteView.as_view(), name='instalacion_delete'),

    # Cargos
    path('cargos/', views.CargoListView.as_view(), name='cargo_list'),
    path('cargos/nuevo/', views.CargoCreateView.as_view(), name='cargo_create'),
    path('cargos/<int:pk>/editar/', views.CargoUpdateView.as_view(), name='cargo_update'),
    path('cargos/<int:pk>/eliminar/', views.CargoDeleteView.as_view(), name='cargo_delete'),

    # Personal
    path('personal/', views.PersonalListView.as_view(), name='personal_list'),
    path('personal/nuevo/', views.PersonalCreateView.as_view(), name='personal_create'),
    path('personal/carga-masiva/', views.PersonalBulkUploadView.as_view(), name='personal_bulk_upload'),
    path('personal/<int:pk>/', views.PersonalDetailView.as_view(), name='personal_detail'),
    path('personal/<int:pk>/editar/', views.PersonalUpdateView.as_view(), name='personal_update'),
    path('personal/<int:pk>/eliminar/', views.PersonalDeleteView.as_view(), name='personal_delete'),
    path('ajax/cargar-instalaciones/', views.ajax_cargar_instalaciones, name='ajax_cargar_instalaciones'),

    # Tipos de Vehículo
    path('tipos-vehiculo/', views.TipoVehiculoListView.as_view(), name='tipo_vehiculo_list'),
    path('tipos-vehiculo/nuevo/', views.TipoVehiculoCreateView.as_view(), name='tipo_vehiculo_create'),
    path('tipos-vehiculo/<int:pk>/editar/', views.TipoVehiculoUpdateView.as_view(), name='tipo_vehiculo_update'),
    path('tipos-vehiculo/<int:pk>/eliminar/', views.TipoVehiculoDeleteView.as_view(), name='tipo_vehiculo_delete'),

    # Vehículos
    path('vehiculos/', views.VehiculoListView.as_view(), name='vehiculo_list'),
    
    # Gestión de Gestores (AJAX)
    path('api/gestores/cliente/', views_gestores.get_gestores_cliente, name='get_gestores_cliente'),
    path('api/gestores/crear/', views_gestores.gestor_create_ajax, name='gestor_create_ajax'),
    path('vehiculos/nuevo/', views.VehiculoCreateView.as_view(), name='vehiculo_create'),
    path('vehiculos/<int:pk>/', views.VehiculoDetailView.as_view(), name='vehiculo_detail'),
    path('vehiculos/<int:pk>/editar/', views.VehiculoUpdateView.as_view(), name='vehiculo_update'),
    path('vehiculos/<int:pk>/eliminar/', views.VehiculoDeleteView.as_view(), name='vehiculo_delete'),

    # Tipos de Incidencia
    path('tipos-incidencia/', views.TipoIncidenciaListView.as_view(), name='tipo_incidencia_list'),
    path('tipos-incidencia/nuevo/', views.TipoIncidenciaCreateView.as_view(), name='tipo_incidencia_create'),
    path('tipos-incidencia/<int:pk>/editar/', views.TipoIncidenciaUpdateView.as_view(), name='tipo_incidencia_update'),
    path('tipos-incidencia/<int:pk>/eliminar/', views.TipoIncidenciaDeleteView.as_view(), name='tipo_incidencia_delete'),

    # Incidencias
    path('incidencias/', views.IncidenciaListView.as_view(), name='incidencia_list'),
    path('incidencias/nueva/', views.IncidenciaCreateView.as_view(), name='incidencia_create'),
    path('incidencias/<int:pk>/', views.IncidenciaDetailView.as_view(), name='incidencia_detail'),
    path('incidencias/<int:pk>/editar/', views.IncidenciaUpdateView.as_view(), name='incidencia_update'),
    path('incidencias/<int:pk>/eliminar/', views.IncidenciaDeleteView.as_view(), name='incidencia_delete'),

    # Turnos
    path('turnos/', views.TurnoListView.as_view(), name='turno_list'),
    path('turnos/nuevo/', views.TurnoCreateView.as_view(), name='turno_create'),
    path('turnos/<int:pk>/', views.TurnoDetailView.as_view(), name='turno_detail'),
    path('turnos/<int:pk>/editar/', views.TurnoUpdateView.as_view(), name='turno_update'),
    path('turnos/<int:pk>/eliminar/', views.TurnoDeleteView.as_view(), name='turno_delete'),
    
    # Configuración de Turnos
    path('configuracion-turnos/', views.ConfiguracionTurnoListView.as_view(), name='configuracion_turno_list'),
    path('configuracion-turnos/nueva/', views.ConfiguracionTurnoCreateView.as_view(), name='configuracion_turno_create'),
    path('configuracion-turnos/<int:pk>/', views.ConfiguracionTurnoDetailView.as_view(), name='configuracion_turno_detail'),
    path('configuracion-turnos/<int:pk>/editar/', views.ConfiguracionTurnoUpdateView.as_view(), name='configuracion_turno_update'),
    path('configuracion-turnos/<int:pk>/eliminar/', views.ConfiguracionTurnoDeleteView.as_view(), name='configuracion_turno_delete'),
]
