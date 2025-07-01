from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView, FormView, View
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django import forms
from django.db.models import Count, Q
from itertools import chain
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from .models import (
    Cliente, Instalacion, Cargo, Personal, TipoVehiculo, Vehiculo, 
    TipoIncidencia, Incidencia, Turno, ConfiguracionTurno, RequerimientosCliente
)
from .forms import PersonalForm, InstalacionForm, RequerimientosInstalacionForm
from django.db.models import Count, Sum
from datetime import datetime, timedelta
import csv
from .utils import get_incidencias_abiertas, get_stats, get_turns_calendar_data

# Mixin vacío para reemplazar LoginRequiredMixin
class NoAuthMixin:
    pass

class DashboardView(TemplateView):
    template_name = 'erp/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener estadísticas
        stats = get_stats()
        context.update(stats)
        
        # Obtener incidencias recientes
        context['incidencias_recentes'] = get_incidencias_abiertas()
        
        return context

class CalendarView(TemplateView):
    template_name = 'erp/calendar.html'
    context_object_name = 'calendar_data'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener fechas del mes actual
        today = datetime.now()
        start_date = today.replace(day=1)
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        # Obtener datos para el calendario
        context['calendar_data'] = get_turns_calendar_data(start_date, end_date)
        
        return context

# Vistas para Gestión Unificada de Clientes e Instalaciones
class GestionClientesView(NoAuthMixin, View):
    template_name = 'erp/gestion_clientes.html'
    
    def get(self, request, *args, **kwargs):
        # Obtener parámetros de búsqueda
        query_cliente = request.GET.get('q_cliente', '')
        query_instalacion = request.GET.get('q_instalacion', '')
        
        # Filtrar clientes
        clientes = Cliente.objects.all().order_by('razon_social')
        if query_cliente:
            clientes = clientes.filter(
                Q(razon_social__icontains=query_cliente) |
                Q(rut__icontains=query_cliente) |
                Q(gestor_nombre__icontains=query_cliente)
            )
        
        # Filtrar instalaciones
        instalaciones = Instalacion.objects.select_related('cliente').order_by('nombre')
        if query_instalacion:
            instalaciones = instalaciones.filter(
                Q(nombre__icontains=query_instalacion) |
                Q(direccion__icontains=query_instalacion) |
                Q(contacto_nombre__icontains=query_instalacion) |
                Q(cliente__razon_social__icontains=query_instalacion)
            )
        
        # Paginación de clientes
        page_cliente = request.GET.get('page_cliente', 1)
        paginator_cliente = Paginator(clientes, 10)
        try:
            clientes_paginated = paginator_cliente.page(page_cliente)
        except (PageNotAnInteger, EmptyPage):
            clientes_paginated = paginator_cliente.page(1)
        
        # Paginación de instalaciones
        page_instalacion = request.GET.get('page_instalacion', 1)
        paginator_instalacion = Paginator(instalaciones, 10)
        try:
            instalaciones_paginated = paginator_instalacion.page(page_instalacion)
        except (PageNotAnInteger, EmptyPage):
            instalaciones_paginated = paginator_instalacion.page(1)
        
        context = {
            'clientes': clientes_paginated,
            'instalaciones': instalaciones_paginated,
            'query_cliente': query_cliente,
            'query_instalacion': query_instalacion,
        }
        
        return render(request, self.template_name, context)

# Vistas para Cliente
class ClienteListView(NoAuthMixin, ListView):
    model = Cliente
    template_name = 'erp/cliente_list.html'
    context_object_name = 'clientes'

class ClienteCreateView(NoAuthMixin, CreateView):
    model = Cliente
    template_name = 'erp/cliente_form.html'
    fields = [
        'razon_social', 'rut', 'direccion', 
        'gestor_nombre', 'gestor_telefono', 'gestor_email',
        'email_contacto', 'telefono_contacto'
    ]
    success_url = reverse_lazy('erp:cliente_list')
    
    def form_valid(self, form):
        print("\n=== INICIO form_valid ===")
        print("Datos del formulario:", form.cleaned_data)
        
        try:
            # Validar campos requeridos
            if not form.cleaned_data.get('razon_social'):
                form.add_error('razon_social', 'La razón social es obligatoria')
                return self.form_invalid(form)
                
            if not form.cleaned_data.get('rut'):
                form.add_error('rut', 'El RUT es obligatorio')
                return self.form_invalid(form)
            
            # Verificar si ya existe un cliente con el mismo RUT
            if Cliente.objects.filter(rut=form.cleaned_data['rut']).exists():
                form.add_error('rut', 'Ya existe un cliente con este RUT')
                return self.form_invalid(form)
            
            # Guardar el formulario
            self.object = form.save(commit=False)
            print("Objeto antes de guardar:", self.object.__dict__)
            
            # Guardar el objeto en la base de datos
            self.object.save()
            print("Objeto guardado con ID:", self.object.id)
            
            # Mostrar mensaje de éxito
            messages.success(
                self.request,
                f'Cliente \"{self.object.razon_social}\" creado exitosamente.'
            )
            print("Mensaje de éxito configurado")
            
            return super().form_valid(form)
            
        except Exception as e:
            print("Error al guardar el cliente:", str(e))
            messages.error(
                self.request,
                f'Error al guardar el cliente: {str(e)}'
            )
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        print("\n=== FORMULARIO INVÁLIDO ===")
        for field, errors in form.errors.items():
            print(f"Error en campo {field}: {', '.join(errors)}")
        return super().form_invalid(form)

class ClienteDetailView(NoAuthMixin, DetailView):
    model = Cliente
    template_name = 'erp/cliente_detail.html'
    context_object_name = 'cliente'

class ClienteUpdateView(NoAuthMixin, UpdateView):
    model = Cliente
    template_name = 'erp/cliente_form.html'
    fields = [
        'razon_social', 'rut', 'direccion', 
        'gestor_nombre', 'gestor_telefono', 'gestor_email',
        'email_contacto', 'telefono_contacto'
    ]
    success_url = reverse_lazy('erp:cliente_list')

class ClienteDeleteView(NoAuthMixin, DeleteView):
    model = Cliente
    template_name = 'erp/cliente_confirm_delete.html'
    success_url = reverse_lazy('erp:cliente_list')

# Vistas para Instalacion
class InstalacionListView(NoAuthMixin, ListView):
    model = Instalacion
    template_name = 'erp/instalacion_list.html'
    context_object_name = 'instalaciones'
    paginate_by = 10  # Mostrar 10 instalaciones por página
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('cliente', 'gestor')
        
        # Filtrar por cliente si se proporciona el parámetro cliente_id
        cliente_id = self.request.GET.get('cliente_id')
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
            
        # Ordenar por nombre de instalación
        return queryset.order_by('nombre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agregar el cliente al contexto si se está filtrando por cliente
        cliente_id = self.request.GET.get('cliente_id')
        if cliente_id:
            try:
                context['cliente'] = Cliente.objects.get(pk=cliente_id)
            except Cliente.DoesNotExist:
                pass
                
        return context

class InstalacionCreateView(NoAuthMixin, CreateView):
    model = Instalacion
    template_name = 'erp/instalacion_form.html'
    form_class = InstalacionForm
    success_url = reverse_lazy('erp:instalacion_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pasar el cliente_id al formulario si está presente en la URL
        cliente_id = self.request.GET.get('cliente')
        if cliente_id:
            kwargs['cliente_id'] = cliente_id
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar el ID del cliente al contexto para usarlo en el template
        cliente_id = self.request.GET.get('cliente')
        if cliente_id:
            context['cliente_id'] = cliente_id
        return context
    
    def form_valid(self, form):
        print("Formulario válido, guardando instalación...")
        try:
            # Guardar la instalación primero
            self.object = form.save(commit=False)
            print(f"Objeto instalación antes de guardar: {self.object}")
            
            # Si hay un cliente_id en la URL, establecerlo como cliente
            cliente_id = self.request.GET.get('cliente')
            if cliente_id and not self.object.cliente_id:
                self.object.cliente_id = cliente_id
                
            self.object.save()
            print(f"Instalación guardada con ID: {self.object.id}")
            
            # Crear los requerimientos por defecto para esta instalación
            requerimientos = RequerimientosCliente.objects.create(
                instalacion=self.object,
                sistema_turnos_4x4=True,  # Valor por defecto
                requiere_personal=True,    # Valor por defecto
                personal_requerido=1,      # Valor por defecto
                personal_por_turno=1,     # Valor por defecto
                requiere_vehiculos=False,  # Valor por defecto
                cantidad_vehiculos=0,      # Valor por defecto
                notas='Configuración inicial creada automáticamente.'
            )
            print(f"Requerimientos creados con ID: {requerimientos.id}")
            
            # Crear configuración de turnos por defecto
            configuracion = ConfiguracionTurno.objects.create(
                requerimientos=requerimientos,
                tipo_turno='4x4',  # Valor por defecto
                turno_mañana_inicio='08:00',
                turno_mañana_fin='20:00',
                turno_tarde_inicio='20:00',
                turno_tarde_fin='08:00',
                dias_trabajo=4,
                dias_descanso=4,
                personal_requerido_por_turno=1,
                incluir_festivos=True,
                notas='Configuración inicial de turnos creada automáticamente.'
            )
            print(f"Configuración de turnos creada con ID: {configuracion.id}")
            
            messages.success(self.request, f'Instalación "{self.object.nombre}" creada exitosamente.')
            return super().form_valid(form)
            
        except Exception as e:
            print(f"Error al crear la instalación: {str(e)}")
            messages.error(self.request, f'Error al crear la instalación: {str(e)}')
            return self.form_invalid(form)

class InstalacionDetailView(NoAuthMixin, DetailView):
    model = Instalacion
    template_name = 'erp/instalacion_detail.html'
    context_object_name = 'instalacion'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener o crear los requerimientos para esta instalación
        requerimientos, created = RequerimientosCliente.objects.get_or_create(
            instalacion=self.object,
            defaults={
                'sistema_turnos_4x4': True,
                'requiere_personal': True,
                'personal_requerido': 1,
                'personal_por_turno': 1,
                'requiere_vehiculos': False,
                'cantidad_vehiculos': 0
            }
        )
        
        # Inicializar el formulario de requerimientos
        if self.request.method == 'POST' and 'requerimientos_form' in self.request.POST:
            requerimientos_form = RequerimientosInstalacionForm(
                self.request.POST, 
                instance=requerimientos,
                prefix='requerimientos'
            )
            if requerimientos_form.is_valid():
                requerimientos_form.save()
                messages.success(self.request, 'Los requerimientos se han actualizado correctamente.')
                return redirect('erp:instalacion_detail', pk=self.object.pk)
        else:
            requerimientos_form = RequerimientosInstalacionForm(
                instance=requerimientos,
                prefix='requerimientos'
            )
        
        # Agregar formulario al contexto
        context['requerimientos_form'] = requerimientos_form
        
        # Obtener estadísticas de personal y vehículos asignados
        context['personal_asignado_count'] = self.object.personal_asignado.count()
        context['vehiculos_asignados_count'] = self.object.vehiculos_asignados.count()
        
        # Calcular cobertura de personal
        if requerimientos.requiere_personal and requerimientos.personal_requerido > 0:
            context['cobertura_personal'] = min(
                (context['personal_asignado_count'] / requerimientos.personal_requerido) * 100,
                100  # Máximo 100%
            )
        else:
            context['cobertura_personal'] = 0
            
        # Calcular cobertura de vehículos
        if requerimientos.requiere_vehiculos and requerimientos.cantidad_vehiculos > 0:
            context['cobertura_vehiculos'] = min(
                (context['vehiculos_asignados_count'] / requerimientos.cantidad_vehiculos) * 100,
                100  # Máximo 100%
            )
        else:
            context['cobertura_vehiculos'] = 0
            
        return context
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener o crear los requerimientos para esta instalación
        requerimientos, created = RequerimientosCliente.objects.get_or_create(
            instalacion=self.object,
            defaults={
                'sistema_turnos_4x4': True,
                'requiere_personal': True,
                'personal_requerido': 1,
                'personal_por_turno': 1,
                'requiere_vehiculos': False,
                'cantidad_vehiculos': 0
            }
        )
        
        # Inicializar el formulario de requerimientos
        if self.request.method == 'POST' and 'requerimientos_form' in self.request.POST:
            requerimientos_form = RequerimientosInstalacionForm(
                self.request.POST, 
                instance=requerimientos,
                prefix='requerimientos'
            )
            if requerimientos_form.is_valid():
                requerimientos_form.save()
                messages.success(self.request, 'Los requerimientos se han actualizado correctamente.')
                return redirect('erp:instalacion_detail', pk=self.object.pk)
        else:
            requerimientos_form = RequerimientosInstalacionForm(
                instance=requerimientos,
                prefix='requerimientos'
            )
        
        # Agregar formulario al contexto
        context['requerimientos_form'] = requerimientos_form
        
        # Obtener estadísticas de personal y vehículos asignados
        context['personal_asignado_count'] = self.object.personal_asignado.count()
        context['vehiculos_asignados_count'] = self.object.vehiculos_asignados.count()
        
        # Calcular cobertura de personal
        if requerimientos.requiere_personal and requerimientos.personal_requerido > 0:
            context['cobertura_personal'] = min(
                (context['personal_asignado_count'] / requerimientos.personal_requerido) * 100,
                100  # Máximo 100%
            )
        else:
            context['cobertura_personal'] = 0
            
        # Calcular cobertura de vehículos
        if requerimientos.requiere_vehiculos and requerimientos.cantidad_vehiculos > 0:
            context['cobertura_vehiculos'] = min(
                (context['vehiculos_asignados_count'] / requerimientos.cantidad_vehiculos) * 100,
                100  # Máximo 100%
            )
        else:
            context['cobertura_vehiculos'] = 0
            
        return context

class InstalacionUpdateView(NoAuthMixin, UpdateView):
    model = Instalacion
    template_name = 'erp/instalacion_form.html'
    fields = ['nombre', 'cliente', 'gestor', 'direccion', 'contacto_nombre', 'contacto_telefono', 'contacto_email', 'activa']
    success_url = reverse_lazy('erp:instalacion_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Si ya hay un cliente seleccionado, filtrar los gestores
        if self.object and self.object.cliente:
            form.fields['gestor'].queryset = self.object.cliente.gestores.all()
        return form
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar el ID del cliente al contexto si existe
        if self.object and self.object.cliente:
            context['cliente_id'] = self.object.cliente.id
        return context

class InstalacionDeleteView(NoAuthMixin, DeleteView):
    model = Instalacion
    template_name = 'erp/instalacion_confirm_delete.html'
    success_url = reverse_lazy('erp:instalacion_list')

# Vistas para Cargo
class CargoListView(NoAuthMixin, ListView):
    model = Cargo
    template_name = 'erp/cargo_list.html'
    context_object_name = 'cargos'

class CargoCreateView(NoAuthMixin, CreateView):
    model = Cargo
    template_name = 'erp/cargo_form.html'
    fields = ['nombre', 'descripcion']
    success_url = reverse_lazy('erp:cargo_list')

class CargoUpdateView(NoAuthMixin, UpdateView):
    model = Cargo
    template_name = 'erp/cargo_form.html'
    fields = ['nombre', 'descripcion']
    success_url = reverse_lazy('erp:cargo_list')

class CargoDeleteView(NoAuthMixin, DeleteView):
    model = Cargo
    template_name = 'erp/cargo_confirm_delete.html'
    success_url = reverse_lazy('erp:cargo_list')

# Vistas para Personal
class PersonalListView(NoAuthMixin, ListView):
    model = Personal
    template_name = 'erp/personal_list.html'
    context_object_name = 'personal'

class PersonalBulkUploadView(NoAuthMixin, FormView):
    template_name = 'erp/personal_bulk_upload.html'
    form_class = forms.Form
    success_url = reverse_lazy('erp:personal_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clientes'] = Cliente.objects.all()
        return context

    def form_valid(self, form):
        # Obtener el archivo CSV
        csv_file = self.request.FILES.get('csv_file')
        if not csv_file:
            form.add_error(None, "Debe seleccionar un archivo CSV")
            return self.form_invalid(form)

        # Validar que el archivo sea CSV
        if not csv_file.name.endswith('.csv'):
            form.add_error(None, "El archivo debe ser un archivo CSV")
            return self.form_invalid(form)

        # Leer el archivo CSV
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            # Validar encabezados
            required_headers = ['nombres', 'apellidos', 'rut', 'fecha_nacimiento', 'direccion', 'telefono', 'email', 'cargo', 'fecha_contratacion', 'cliente']
            missing_headers = [h for h in required_headers if h not in reader.fieldnames]
            if missing_headers:
                form.add_error(None, f"Faltan los siguientes campos en el CSV: {', '.join(missing_headers)}")
                return self.form_invalid(form)

            # Procesar cada fila
            for row in reader:
                try:
                    # Buscar cliente
                    cliente = Cliente.objects.get(razon_social=row['cliente'])
                    
                    # Buscar cargo
                    cargo, _ = Cargo.objects.get_or_create(nombre=row['cargo'])
                    
                    # Convertir fechas de DD-MM-YYYY a YYYY-MM-DD
                    fecha_nacimiento = datetime.strptime(row['fecha_nacimiento'], '%d-%m-%Y')
                    fecha_contratacion = datetime.strptime(row['fecha_contratacion'], '%d-%m-%Y')
                    
                    # Crear personal
                    personal = Personal.objects.create(
                        cliente=cliente,
                        nombres=row['nombres'],
                        apellidos=row['apellidos'],
                        rut=row['rut'],
                        fecha_nacimiento=fecha_nacimiento,
                        direccion=row['direccion'],
                        telefono=row['telefono'],
                        email=row['email'],
                        cargo=cargo,
                        fecha_contratacion=fecha_contratacion,
                        activo=True
                    )
                except Exception as e:
                    form.add_error(None, f"Error procesando la fila: {str(e)}")
                    return self.form_invalid(form)

            messages.success(self.request, "Personal cargado exitosamente")
            return super().form_valid(form)
        except Exception as e:
            form.add_error(None, f"Error leyendo el archivo: {str(e)}")
            return self.form_invalid(form)

class PersonalCreateView(NoAuthMixin, CreateView):
    model = Personal
    form_class = PersonalForm
    template_name = 'erp/personal_form.html'
    success_url = reverse_lazy('erp:personal_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Personal creado exitosamente.')
        return response

class PersonalDetailView(NoAuthMixin, DetailView):
    model = Personal
    template_name = 'erp/personal_detail.html'
    context_object_name = 'persona'

class PersonalUpdateView(NoAuthMixin, UpdateView):
    model = Personal
    form_class = PersonalForm
    template_name = 'erp/personal_form.html'
    success_url = reverse_lazy('erp:personal_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Personal actualizado exitosamente.')
        return response

class PersonalDeleteView(NoAuthMixin, DeleteView):
    model = Personal
    template_name = 'erp/personal_confirm_delete.html'
    success_url = reverse_lazy('erp:personal_list')

# Vistas para TipoVehiculo
class TipoVehiculoListView(NoAuthMixin, ListView):
    model = TipoVehiculo
    template_name = 'erp/tipo_vehiculo_list.html'
    context_object_name = 'tipos_vehiculo'

class TipoVehiculoCreateView(NoAuthMixin, CreateView):
    model = TipoVehiculo
    template_name = 'erp/tipo_vehiculo_form.html'
    fields = ['nombre']
    success_url = reverse_lazy('erp:tipo_vehiculo_list')

class TipoVehiculoUpdateView(NoAuthMixin, UpdateView):
    model = TipoVehiculo
    template_name = 'erp/tipo_vehiculo_form.html'
    fields = ['nombre']
    success_url = reverse_lazy('erp:tipo_vehiculo_list')

class TipoVehiculoDeleteView(NoAuthMixin, DeleteView):
    model = TipoVehiculo
    template_name = 'erp/tipo_vehiculo_confirm_delete.html'
    success_url = reverse_lazy('erp:tipo_vehiculo_list')

# Vistas para Vehiculo
class VehiculoListView(NoAuthMixin, ListView):
    model = Vehiculo
    template_name = 'erp/vehiculo_list.html'
    context_object_name = 'vehiculos'

class VehiculoCreateView(NoAuthMixin, CreateView):
    model = Vehiculo
    template_name = 'erp/vehiculo_form.html'
    fields = ['patente', 'marca', 'modelo', 'ano', 'tipo', 'kilometraje', 'en_servicio', 'instalacion_asignada']
    success_url = reverse_lazy('erp:vehiculo_list')

class VehiculoDetailView(NoAuthMixin, DetailView):
    model = Vehiculo
    template_name = 'erp/vehiculo_detail.html'
    context_object_name = 'vehiculo'

class VehiculoUpdateView(NoAuthMixin, UpdateView):
    model = Vehiculo
    template_name = 'erp/vehiculo_form.html'
    fields = ['patente', 'marca', 'modelo', 'ano', 'tipo', 'kilometraje', 'en_servicio', 'instalacion_asignada']
    success_url = reverse_lazy('erp:vehiculo_list')

class VehiculoDeleteView(NoAuthMixin, DeleteView):
    model = Vehiculo
    template_name = 'erp/vehiculo_confirm_delete.html'
    success_url = reverse_lazy('erp:vehiculo_list')

# Vistas para TipoIncidencia
class TipoIncidenciaListView(NoAuthMixin, ListView):
    model = TipoIncidencia
    template_name = 'erp/tipo_incidencia_list.html'
    context_object_name = 'tipos_incidencia'

class TipoIncidenciaCreateView(NoAuthMixin, CreateView):
    model = TipoIncidencia
    template_name = 'erp/tipo_incidencia_form.html'
    fields = ['nombre', 'descripcion']
    success_url = reverse_lazy('erp:tipo_incidencia_list')

class TipoIncidenciaUpdateView(NoAuthMixin, UpdateView):
    model = TipoIncidencia
    template_name = 'erp/tipo_incidencia_form.html'
    fields = ['nombre', 'descripcion']
    success_url = reverse_lazy('erp:tipo_incidencia_list')

class TipoIncidenciaDeleteView(NoAuthMixin, DeleteView):
    model = TipoIncidencia
    template_name = 'erp/tipo_incidencia_confirm_delete.html'
    success_url = reverse_lazy('erp:tipo_incidencia_list')

# Vistas para Incidencia
class IncidenciaListView(NoAuthMixin, ListView):
    model = Incidencia
    template_name = 'erp/incidencia_list.html'
    context_object_name = 'incidencias'

class IncidenciaCreateView(NoAuthMixin, CreateView):
    model = Incidencia
    template_name = 'erp/incidencia_form.html'
    fields = ['titulo', 'instalacion', 'tipo_incidencia', 'fecha_hora_suceso', 'descripcion', 'personal_involucrado']
    success_url = reverse_lazy('erp:incidencia_list')

class IncidenciaDetailView(NoAuthMixin, DetailView):
    model = Incidencia
    template_name = 'erp/incidencia_detail.html'
    context_object_name = 'incidencia'

class IncidenciaUpdateView(NoAuthMixin, UpdateView):
    model = Incidencia
    template_name = 'erp/incidencia_form.html'
    fields = ['titulo', 'instalacion', 'tipo_incidencia', 'fecha_hora_suceso', 'descripcion', 'personal_involucrado']
    success_url = reverse_lazy('erp:incidencia_list')

class IncidenciaDeleteView(NoAuthMixin, DeleteView):
    model = Incidencia
    template_name = 'erp/incidencia_confirm_delete.html'
    success_url = reverse_lazy('erp:incidencia_list')

# Vistas para Configuración de Turnos
class ConfiguracionTurnoListView(NoAuthMixin, ListView):
    model = ConfiguracionTurno
    template_name = 'erp/configuracion_turno_list.html'
    context_object_name = 'configuraciones'

class ConfiguracionTurnoCreateView(NoAuthMixin, CreateView):
    model = ConfiguracionTurno
    template_name = 'erp/configuracion_turno_form.html'
    fields = ['instalacion', 'tipo_turno', 'hora_inicio', 'hora_fin', 'dias_libres', 'dias_trabajo', 'activo']
    success_url = reverse_lazy('erp:configuracion_turno_list')

class ConfiguracionTurnoDetailView(NoAuthMixin, DetailView):
    model = ConfiguracionTurno
    template_name = 'erp/configuracion_turno_detail.html'
    context_object_name = 'configuracion'

class ConfiguracionTurnoUpdateView(NoAuthMixin, UpdateView):
    model = ConfiguracionTurno
    template_name = 'erp/configuracion_turno_form.html'
    fields = ['instalacion', 'tipo_turno', 'hora_inicio', 'hora_fin', 'dias_libres', 'dias_trabajo', 'activo']
    success_url = reverse_lazy('erp:configuracion_turno_list')

class ConfiguracionTurnoDeleteView(NoAuthMixin, DeleteView):
    model = ConfiguracionTurno
    template_name = 'erp/configuracion_turno_confirm_delete.html'
    success_url = reverse_lazy('erp:configuracion_turno_list')

# Vistas para Turno
class TurnoListView(NoAuthMixin, ListView):
    model = Turno
    template_name = 'erp/turno_list.html'
    context_object_name = 'turnos'

class TurnoCreateView(NoAuthMixin, CreateView):
    model = Turno
    template_name = 'erp/turno_form.html'
    fields = ['personal', 'instalacion', 'fecha_inicio', 'fecha_fin', 'tipo_turno']
    success_url = reverse_lazy('erp:turno_list')

class TurnoDetailView(NoAuthMixin, DetailView):
    model = Turno
    template_name = 'erp/turno_detail.html'
    context_object_name = 'turno'

class TurnoUpdateView(NoAuthMixin, UpdateView):
    model = Turno
    template_name = 'erp/turno_form.html'
    fields = ['personal', 'instalacion', 'fecha_inicio', 'fecha_fin', 'tipo_turno']
    success_url = reverse_lazy('erp:turno_list')

class TurnoDeleteView(NoAuthMixin, DeleteView):
    model = Turno
    template_name = 'erp/turno_confirm_delete.html'
    success_url = reverse_lazy('erp:turno_list')


def ajax_cargar_instalaciones(request):
    """Vista para cargar dinámicamente las instalaciones de un cliente"""
    cliente_id = request.GET.get('cliente_id')
    
    if not cliente_id:
        return JsonResponse({'error': 'No se proporcionó un ID de cliente'}, status=400)
    
    try:
        # Filtrar instalaciones activas del cliente
        instalaciones = Instalacion.objects.filter(
            cliente_id=cliente_id,
            activa=True
        ).values('id', 'nombre')
        
        # Convertir el queryset a lista para serialización
        instalaciones_list = list(instalaciones)
        
        return JsonResponse({
            'instalaciones': instalaciones_list
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
