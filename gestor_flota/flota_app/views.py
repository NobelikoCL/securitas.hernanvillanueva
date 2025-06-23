from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
import pandas as pd
from io import BytesIO
import os
from django.core.files.base import ContentFile
from django.http import HttpResponse, FileResponse
from django.conf import settings
import tempfile
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

from .models import Vehiculo, Personal, Instalacion, Turno, AsignacionVehiculo, AsignacionInstalacion, GestionTransporte, CentroCosto
from .forms import VehiculoForm, PersonalForm, FileUploadForm

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
        
        # Crear plantilla de ejemplo si no existe
        template_path = os.path.join(settings.MEDIA_ROOT, 'plantillas', 'plantilla_carga_masiva_personal.xlsx')
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        
        # Si el archivo no existe o se solicita regenerar
        if not os.path.exists(template_path) or request.GET.get('regenerar'):
            self.generar_plantilla_ejemplo(template_path)
        
        context = {
            'form': form,
            'titulo_pagina': "Carga Masiva de Personal",
            'ejemplo_archivo': os.path.join(settings.MEDIA_URL, 'plantillas/plantilla_carga_masiva_personal.xlsx')
        }
        return render(request, self.template_name, context)
    
    def generar_plantilla_ejemplo(self, filepath):
        """Genera un archivo Excel de ejemplo para la carga masiva de personal"""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Personal"
        
        # Estilos para la cabecera
        header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
        # Columnas requeridas
        headers = [
            "nombre", "apellido", "rut", "fecha_nacimiento", "direccion",
            "telefono_contacto", "acepta_mensajeria_whatsapp", "legajo",
            "fecha_ingreso", "instalacion_trabajo", "centro_costo"
        ]
        
        # Escribir encabezados
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment
            
            # Ajustar ancho de columna
            column_letter = get_column_letter(col_num)
            ws.column_dimensions[column_letter].width = max(len(header) + 2, 15)
        
        # Agregar fila de ejemplo
        ejemplo = [
            "Juan", "Pérez González", "12.345.678-9", "1985-05-15", "Av. Principal 1234",
            "912345678", "SI", "EMP-001", "2023-01-15", "Oficina Central", "CC-001"
        ]
        
        for col_num, value in enumerate(ejemplo, 1):
            cell = ws.cell(row=2, column=col_num, value=value)
            if headers[col_num-1] in ['fecha_nacimiento', 'fecha_ingreso']:
                cell.number_format = 'YYYY-MM-DD'
        
        # Agregar validación de datos
        dv = openpyxl.worksheet.datavalidation.DataValidation(
            type="list",
            formula1='"SI,NO"',
            showErrorMessage=True,
            errorTitle='Valor no válido',
            error='Debe ser SI o NO',
            showDropDown=True
        )
        dv.add(f'G2:G1048576')  # Para la columna acepta_mensajeria_whatsapp
        ws.add_data_validation(dv)
        
        # Guardar el archivo
        wb.save(filepath)
        return filepath

    def post(self, request, *args, **kwargs):
        form = FileUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")
            return self.get(request, *args, **kwargs)
            
        file = request.FILES['file']
        file_extension = os.path.splitext(file.name)[1].lower()
        
        try:
            # Leer el archivo según su extensión
            if file_extension == '.csv':
                df = pd.read_csv(file, dtype=str, encoding='utf-8')
            elif file_extension in ['.xls', '.xlsx']:
                df = pd.read_excel(file, dtype=str, engine='openpyxl')
            else:
                messages.error(request, "Formato de archivo no soportado. Use archivos CSV o Excel (XLSX).")
                return redirect('flota_app:personal_bulk_upload')

            # Eliminar filas completamente vacías
            df = df.dropna(how='all')
            
            # Verificar si el archivo está vacío
            if df.empty:
                messages.error(request, "El archivo está vacío o no contiene datos válidos.")
                return redirect('flota_app:personal_bulk_upload')

            # Normalizar nombres de columnas (quitar espacios, a minúsculas, sin caracteres especiales)
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
            
            # Verificar columnas requeridas
            required_columns = [
                'nombre', 'apellido', 'rut', 'fecha_nacimiento', 
                'direccion', 'telefono_contacto', 'acepta_mensajeria_whatsapp', 
                'legajo', 'fecha_ingreso'
            ]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                messages.error(
                    request, 
                    f"Faltan las siguientes columnas obligatorias: {', '.join(missing_columns)}. "
                    f"Por favor, descargue la plantilla de ejemplo para ver el formato correcto."
                )
                return redirect('flota_app:personal_bulk_upload')

            errors = []
            success_count = 0
            
            # Listas para almacenar datos de éxito y advertencias
            success_list = []
            warning_list = []
            
            # Obtener todas las instalaciones y centros de costo para validación
            instalaciones = {inst.nombre.lower().strip(): inst for inst in Instalacion.objects.all()}
            centros_costo = {str(cc.codigo).lower().strip(): cc for cc in CentroCosto.objects.all()}
            
            # Validar cada fila del archivo
            for index, row in df.iterrows():
                row_errors = []
                row_num = index + 2  # +2 porque Excel comienza en 1 y la primera fila es el encabezado
                
                # Validar campos obligatorios
                for col in required_columns:
                    if pd.isna(row.get(col, '')) or str(row[col]).strip() == '':
                        row_errors.append(f"La columna '{col}' es obligatoria")
                
                # Validar formato de RUT
                rut = str(row.get('rut', '')).strip()
                if rut:
                    # Validar formato básico de RUT (acepta con o sin puntos/guion)
                    import re
                    if not re.match(r'^\d{1,3}(?:\.?\d{3}){2}-[\dkK]$', rut):
                        row_errors.append("Formato de RUT inválido. Debe ser como 12.345.678-9 o 12345678-9")
                
                # Validar fechas
                for date_col in ['fecha_nacimiento', 'fecha_ingreso']:
                    date_str = str(row.get(date_col, '')).strip()
                    if date_str:
                        try:
                            datetime.strptime(date_str, '%Y-%m-%d').date()
                        except ValueError:
                            row_errors.append(f"Formato de fecha inválido en {date_col}. Use YYYY-MM-DD")
                
                # Validar teléfono
                telefono = str(row.get('telefono_contacto', '')).strip()
                if telefono and not telefono.isdigit():
                    row_errors.append("El teléfono debe contener solo números")
                
                # Validar SI/NO para WhatsApp
                whatsapp = str(row.get('acepta_mensajeria_whatsapp', '')).strip().upper()
                if whatsapp not in ['SI', 'NO']:
                    row_errors.append("El campo 'acepta_mensajeria_whatsapp' debe ser 'SI' o 'NO'")
                
                # Validar instalación de trabajo
                instalacion_nombre = str(row.get('instalacion_trabajo', '')).strip().lower()
                if instalacion_nombre and instalacion_nombre not in instalaciones:
                    row_errors.append(f"Instalación de trabajo no encontrada: {row.get('instalacion_trabajo')}")
                
                # Validar centro de costo
                centro_costo_codigo = str(row.get('centro_costo', '')).strip().lower()
                if centro_costo_codigo and centro_costo_codigo not in centros_costo:
                    row_errors.append(f"Centro de costo no encontrado: {row.get('centro_costo')}")
                
                if row_errors:
                    errors.append({
                        'fila': row_num,
                        'errores': row_errors,
                        'datos': row.to_dict()
                    })
                    continue
                
                # Si llegamos aquí, la fila es válida
                try:
                    with transaction.atomic():
                        # Crear o actualizar el personal
                        personal_data = {
                            'nombre': str(row['nombre']).strip(),
                            'apellido': str(row['apellido']).strip(),
                            'rut': rut.replace('.', '').replace('-', '').upper(),
                            'fecha_nacimiento': datetime.strptime(str(row['fecha_nacimiento']).strip(), '%Y-%m-%d').date(),
                            'direccion': str(row['direccion']).strip(),
                            'telefono_contacto': telefono,
                            'acepta_mensajeria_whatsapp': whatsapp == 'SI',
                            'legajo': str(row['legajo']).strip(),
                            'fecha_ingreso': datetime.strptime(str(row['fecha_ingreso']).strip(), '%Y-%m-%d').date(),
                        }
                        
                        # Asignar instalación si existe
                        if instalacion_nombre:
                            personal_data['instalacion_trabajo'] = instalaciones[instalacion_nombre]
                        
                        # Asignar centro de costo si existe
                        if centro_costo_codigo:
                            personal_data['centro_costo'] = centros_costo[centro_costo_codigo]
                        
                        # Verificar si ya existe un personal con el mismo RUT o legajo
                        personal_existente = Personal.objects.filter(
                            rut=personal_data['rut']
                        ).first()
                        
                        if personal_existente:
                            # Actualizar registro existente
                            for key, value in personal_data.items():
                                setattr(personal_existente, key, value)
                            personal_existente.save()
                            success_list.append(f"Fila {row_num}: Actualizado {personal_data['nombre']} {personal_data['apellido']} (RUT: {personal_data['rut']})")
                        else:
                            # Crear nuevo registro
                            personal = Personal.objects.create(**personal_data)
                            success_list.append(f"Fila {row_num}: Creado {personal.nombre} {personal.apellido} (RUT: {personal.rut})")
                        
                        success_count += 1
                        
                except Exception as e:
                    error_msg = f"Error en fila {row_num}: {str(e)}"
                    errors.append({
                        'fila': row_num,
                        'errores': [error_msg],
                        'datos': row.to_dict()
                    })
            
            # Preparar mensajes de resultado
            if success_count > 0:
                success_message = f"Se procesaron correctamente {success_count} registros."
                if len(success_list) > 5:
                    success_message += "<br>" + "<br>".join(success_list[:5])
                    success_message += f"<br>... y {len(success_list) - 5} más"
                else:
                    success_message += "<br>" + "<br>".join(success_list)
                messages.success(request, success_message, extra_tags='safe')
            
            if errors:
                error_message = f"Se encontraron {len(errors)} errores en el archivo:"
                for i, error in enumerate(errors[:5], 1):
                    error_message += f"<br>{i}. Fila {error['fila']}: {', '.join(error['errores'])}"
                if len(errors) > 5:
                    error_message += f"<br>... y {len(errors) - 5} errores más"
                messages.error(request, error_message, extra_tags='safe')
            
            return redirect('flota_app:personal_bulk_upload')
            
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {str(e)}")
            return redirect('flota_app:personal_bulk_upload')

        # Si el formulario no es válido, mostrar errores
        messages.error(request, "Por favor, corrija los errores en el formulario.")
        return redirect('flota_app:personal_bulk_upload')
