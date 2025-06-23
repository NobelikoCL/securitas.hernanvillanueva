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

    # Próximamente más URLs para otras funcionalidades
]
