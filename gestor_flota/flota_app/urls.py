from django.urls import path
from . import views

app_name = 'flota_app'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'), # Nueva URL para el dashboard
    path('vehiculos/', views.VehiculoListView.as_view(), name='vehiculo_list'),
    path('vehiculos/nuevo/', views.VehiculoCreateView.as_view(), name='vehiculo_create'),
    path('vehiculos/<int:pk>/editar/', views.VehiculoUpdateView.as_view(), name='vehiculo_update'),
    path('vehiculos/<int:pk>/eliminar/', views.VehiculoDeleteView.as_view(), name='vehiculo_delete'),

    # URLs para Personal
    path('personal/', views.PersonalListView.as_view(), name='personal_list'),
    path('personal/nuevo/', views.PersonalCreateView.as_view(), name='personal_create'),
    path('personal/<int:pk>/', views.PersonalDetailView.as_view(), name='personal_detail'),
    path('personal/<int:pk>/editar/', views.PersonalUpdateView.as_view(), name='personal_update'),
    path('personal/<int:pk>/eliminar/', views.PersonalDeleteView.as_view(), name='personal_delete'),
    path('personal/carga_masiva/', views.PersonalBulkUploadView.as_view(), name='personal_bulk_upload'),

    # URLs para Cliente (CRUD)
    path('clientes/', views.ClienteListView.as_view(), name='cliente_list'),
    path('clientes/nuevo/', views.ClienteCreateView.as_view(), name='cliente_create'),
    path('clientes/<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='cliente_update'),
    path('clientes/<int:pk>/eliminar/', views.ClienteDeleteView.as_view(), name='cliente_delete'),
    # path('clientes/<int:pk>/', views.ClienteDetailView.as_view(), name='cliente_detail'), # Si se implementa una DetailView

    # URLs para CentroCosto (anidadas bajo cliente)
    path('cliente/<int:cliente_id>/centros_costo/', views.CentroCostoListView.as_view(), name='centrocosto_list_by_cliente'),
    path('cliente/<int:cliente_id>/centros_costo/nuevo/', views.CentroCostoCreateView.as_view(), name='centrocosto_create_for_cliente'),
    # Para editar y eliminar, el pk del CentroCosto es suficiente, pero las vistas se ajustarán para el contexto.
    # Podríamos mantenerlas así o anidarlas también si queremos reforzar el contexto del cliente en la URL.
    # Por ahora, las dejamos con pk de CC, y la vista se asegurará que el CC pertenezca al cliente si es necesario.
    path('centros_costo/<int:pk>/editar/', views.CentroCostoUpdateView.as_view(), name='centrocosto_update'), # La vista necesitará contexto de cliente si se accede desde un cliente
    path('centros_costo/<int:pk>/eliminar/', views.CentroCostoDeleteView.as_view(), name='centrocosto_delete'),# Idem

    # URLs para Instalacion (anidadas bajo cliente y centro_costo)
    # Lista de instalaciones para un cliente específico (puede ser filtrada por CC en la vista con GET param)
    path('cliente/<int:cliente_id>/instalaciones/', views.InstalacionListView.as_view(), name='instalacion_list_by_cliente'),
    # Lista de instalaciones para un centro de costo específico (que pertenece a un cliente)
    path('cliente/<int:cliente_id>/centro_costo/<int:centro_costo_id>/instalaciones/', views.InstalacionListView.as_view(), name='instalacion_list_by_cc'),
    path('cliente/<int:cliente_id>/centro_costo/<int:centro_costo_id>/instalaciones/nuevo/', views.InstalacionCreateView.as_view(), name='instalacion_create_for_cc'),
    # Para editar y eliminar, pk de Instalacion es suficiente. La vista se asegurará del contexto.
    path('instalaciones/<int:pk>/editar/', views.InstalacionUpdateView.as_view(), name='instalacion_update'),
    path('instalaciones/<int:pk>/eliminar/', views.InstalacionDeleteView.as_view(), name='instalacion_delete'),

    # URLs "globales" (no anidadas) si se necesitan para roles de admin, por ejemplo
    # path('centros_costo/todos/', views.CentroCostoListView.as_view(), name='centrocosto_list_all'), # Ejemplo, si se mantiene
    # path('instalaciones/todas/', views.InstalacionListView.as_view(), name='instalacion_list_all'), # Ejemplo

    # Próximamente más URLs para otras funcionalidades
]
