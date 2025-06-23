from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from .models import Vehiculo, Personal
from .forms import VehiculoForm, PersonalForm

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

def dashboard_view(request):
    context = {
        'titulo_pagina': "Dashboard Principal"
    }
    return render(request, 'flota_app/dashboard.html', context)

# Vistas para Personal
class PersonalListView(ListView):
    model = Personal
    template_name = 'flota_app/personal_list.html'
    context_object_name = 'personal_list' # Cambiado para evitar conflicto con 'personal' si se usa en el contexto

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = "Listado de Personal"
        return context

class PersonalDetailView(DetailView):
    model = Personal
    template_name = 'flota_app/personal_detail.html'
    context_object_name = 'personal'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f"Detalle de {self.object.nombre} {self.object.apellido}"
        return context

class PersonalCreateView(CreateView):
    model = Personal
    form_class = PersonalForm
    template_name = 'flota_app/personal_form.html'
    success_url = reverse_lazy('flota_app:personal_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = "Añadir Personal"
        context['es_creacion'] = True # Para diferenciar en la plantilla si es necesario
        return context

class PersonalUpdateView(UpdateView):
    model = Personal
    form_class = PersonalForm
    template_name = 'flota_app/personal_form.html'
    success_url = reverse_lazy('flota_app:personal_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f"Editar Personal: {self.object.nombre} {self.object.apellido}"
        context['es_creacion'] = False
        return context

class PersonalDeleteView(DeleteView):
    model = Personal
    template_name = 'flota_app/personal_confirm_delete.html'
    success_url = reverse_lazy('flota_app:personal_list')
    context_object_name = 'personal'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f"Confirmar Eliminación de {self.object.nombre} {self.object.apellido}"
        return context

import pandas as pd
from django.shortcuts import redirect
from django.contrib import messages
from django.views import View
from .forms import FileUploadForm
from .models import Instalacion, CentroCosto # Asegúrate que User esté importado si lo usas directamente
from django.contrib.auth.models import User
from datetime import datetime

class PersonalBulkUploadView(View):
    template_name = 'flota_app/personal_bulk_upload.html'

    def get(self, request, *args, **kwargs):
        form = FileUploadForm()
        return render(request, self.template_name, {'form': form, 'titulo_pagina': "Carga Masiva de Personal"})

    def post(self, request, *args, **kwargs):
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file, dtype=str) # Leer todo como string inicialmente
                elif file.name.endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(file, dtype=str) # Leer todo como string inicialmente
                else:
                    messages.error(request, "Formato de archivo no soportado. Use CSV o Excel.")
                    return redirect('flota_app:personal_bulk_upload')

                # Normalizar nombres de columnas (ej. quitar espacios, a minúsculas)
                df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

                required_columns = ['nombre', 'apellido', 'rut', 'fecha_nacimiento', 'direccion',
                                    'telefono_contacto', 'acepta_mensajeria_whatsapp', 'legajo',
                                    'fecha_ingreso']

                # Verificar columnas mínimas
                missing_cols = [col for col in required_columns if col not in df.columns]
                if missing_cols:
                    messages.error(request, f"Faltan las siguientes columnas obligatorias: {', '.join(missing_cols)}")
                    return redirect('flota_app:personal_bulk_upload')

                errors = []
                success_count = 0

                for index, row in df.iterrows():
                    try:
                        # Validaciones y obtención de datos
                        nombre = row.get('nombre')
                        apellido = row.get('apellido')
                        rut = row.get('rut')
                        legajo = row.get('legajo')

                        if not all([nombre, apellido, rut, legajo]):
                            errors.append(f"Fila {index + 2}: Nombre, apellido, RUT y legajo son obligatorios.")
                            continue

                        # Limpiar RUT: quitar puntos y guion si los tiene para la validación/guardado.
                        # Esto depende de cómo quieras almacenar el RUT. Si lo quieres con formato, ajusta.
                        rut_cleaned = str(rut).replace('.', '').replace('-', '').strip()
                        # Aquí podrías añadir una validación de formato de RUT si es necesario

                        if Personal.objects.filter(rut=rut_cleaned).exists() or Personal.objects.filter(legajo=legajo).exists():
                            errors.append(f"Fila {index + 2}: Personal con RUT {rut} o legajo {legajo} ya existe.")
                            continue

                        fecha_nac_str = row.get('fecha_nacimiento')
                        fecha_ing_str = row.get('fecha_ingreso')

                        try:
                            fecha_nacimiento = datetime.strptime(fecha_nac_str, '%Y-%m-%d').date() if fecha_nac_str else None
                        except ValueError:
                            errors.append(f"Fila {index + 2}: Formato de fecha_nacimiento incorrecto para '{fecha_nac_str}'. Usar YYYY-MM-DD.")
                            continue

                        try:
                            fecha_ingreso = datetime.strptime(fecha_ing_str, '%Y-%m-%d').date() if fecha_ing_str else None
                        except ValueError:
                             errors.append(f"Fila {index + 2}: Formato de fecha_ingreso incorrecto para '{fecha_ing_str}'. Usar YYYY-MM-DD.")
                             continue

                        if not fecha_nacimiento or not fecha_ingreso:
                            errors.append(f"Fila {index + 2}: fecha_nacimiento y fecha_ingreso son obligatorias.")
                            continue


                        acepta_whatsapp_str = str(row.get('acepta_mensajeria_whatsapp', 'NO')).strip().upper()
                        acepta_whatsapp = acepta_whatsapp_str == 'SI'

                        personal_data = {
                            'nombre': nombre,
                            'apellido': apellido,
                            'rut': rut_cleaned, # Guardar RUT limpio o formateado según tu modelo
                            'fecha_nacimiento': fecha_nacimiento,
                            'direccion': row.get('direccion', ''),
                            'telefono_contacto': row.get('telefono_contacto', ''),
                            'acepta_mensajeria_whatsapp': acepta_whatsapp,
                            'legajo': legajo,
                            'fecha_ingreso': fecha_ingreso,
                        }

                        # Instalacion
                        instalacion_nombre = row.get('instalacion_trabajo_nombre')
                        if instalacion_nombre:
                            try:
                                instalacion = Instalacion.objects.get(nombre__iexact=instalacion_nombre.strip())
                                personal_data['instalacion_trabajo'] = instalacion
                            except Instalacion.DoesNotExist:
                                errors.append(f"Fila {index + 2}: Instalación '{instalacion_nombre}' no encontrada.")
                                # Decidir si continuar sin instalación o detenerse

                        # Centro de Costo
                        cc_codigo = row.get('centro_costo_codigo')
                        if cc_codigo:
                            try:
                                centro_costo = CentroCosto.objects.get(codigo__iexact=cc_codigo.strip())
                                personal_data['centro_costo'] = centro_costo
                            except CentroCosto.DoesNotExist:
                                errors.append(f"Fila {index + 2}: Centro de Costo con código '{cc_codigo}' no encontrado.")
                                # Decidir si continuar sin CC o detenerse

                        # Usuario (opcional)
                        username = row.get('usuario_username')
                        if username:
                            try:
                                user = User.objects.get(username__iexact=username.strip())
                                personal_data['usuario'] = user
                            except User.DoesNotExist:
                                errors.append(f"Fila {index + 2}: Usuario '{username}' no encontrado. El personal se creará sin usuario asociado.")

                        Personal.objects.create(**personal_data)
                        success_count += 1

                    except Exception as e:
                        errors.append(f"Fila {index + 2}: Error al procesar - {e}")

                if success_count > 0:
                    messages.success(request, f"{success_count} registros de personal importados exitosamente.")
                if errors:
                    error_message = "Se encontraron los siguientes errores durante la importación:<br>" + "<br>".join(errors)
                    messages.warning(request, error_message) # Usar warning para errores no críticos que permitieron continuar

            except Exception as e:
                messages.error(request, f"Error al procesar el archivo: {e}")

            return redirect('flota_app:personal_bulk_upload')

        return render(request, self.template_name, {'form': form, 'titulo_pagina': "Carga Masiva de Personal"})
