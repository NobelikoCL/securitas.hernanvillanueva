from django.urls import path
from . import views

app_name = 'flota_app'

urlpatterns = [
    path('vehiculos/', views.VehiculoListView.as_view(), name='vehiculo_list'),
    # Próximamente más URLs para otras funcionalidades
]
