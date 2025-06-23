from django.shortcuts import render
from django.views.generic import ListView
from .models import Vehiculo

class VehiculoListView(ListView):
    model = Vehiculo
    template_name = 'flota_app/vehiculo_list.html' # Especificaremos esta plantilla a continuación
    context_object_name = 'vehiculos'

from django.utils.translation import gettext_lazy as _

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = _("Listado de Vehículos") # Marcado para traducción
        return context

# Más vistas se añadirán aquí para otras funcionalidades.
