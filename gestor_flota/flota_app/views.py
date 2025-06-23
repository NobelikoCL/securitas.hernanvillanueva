from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Vehiculo
from .forms import VehiculoForm

class VehiculoListView(ListView):
    model = Vehiculo
    template_name = 'flota_app/vehiculo_list.html'
    context_object_name = 'vehiculos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = "Listado de Vehículos"
        return context

class VehiculoCreateView(CreateView):
    model = Vehiculo
    form_class = VehiculoForm
    template_name = 'flota_app/vehiculo_form.html'
    success_url = reverse_lazy('flota_app:vehiculo_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = "Añadir Vehículo"
        return context

class VehiculoUpdateView(UpdateView):
    model = Vehiculo
    form_class = VehiculoForm
    template_name = 'flota_app/vehiculo_form.html'
    success_url = reverse_lazy('flota_app:vehiculo_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = "Editar Vehículo"
        return context

class VehiculoDeleteView(DeleteView):
    model = Vehiculo
    template_name = 'flota_app/vehiculo_confirm_delete.html'
    success_url = reverse_lazy('flota_app:vehiculo_list')
    context_object_name = 'vehiculo' # Para usar {{ vehiculo }} en la plantilla

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = "Confirmar Eliminación de Vehículo"
        return context

# Más vistas se añadirán aquí para otras funcionalidades.
