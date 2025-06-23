from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Vehiculo
import re

def validar_rut(rut):
    """Valida el formato del RUT chileno."""
    rut = rut.upper().replace('.', '').replace('-', '')
    if not re.match(r'^\d{7,8}[0-9K]$', rut):
        raise ValidationError(_('El RUT ingresado no tiene un formato válido.'))
    
    # Validar dígito verificador
    cuerpo = rut[:-1]
    dv = rut[-1]
    
    suma = 0
    multiplo = 2
    
    # Calcular dígito verificador
    for i in reversed(cuerpo):
        suma += int(i) * multiplo
        multiplo += 1
        if multiplo > 7:
            multiplo = 2
    
    resto = suma % 11
    dv_esperado = 11 - resto if resto > 1 else 'K' if resto == 10 else '0'
    
    if str(dv_esperado) != dv:
        raise ValidationError(_('El RUT ingresado no es válido.'))
    
    return rut

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['patente', 'marca', 'modelo', 'año', 'kilometraje', 'en_reparacion']
        widgets = {
            'patente': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'año': forms.NumberInput(attrs={'class': 'form-control'}),
            'kilometraje': forms.NumberInput(attrs={'class': 'form-control'}),
            'en_reparacion': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'año': 'Año',
            'en_reparacion': 'En Reparación',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap no maneja bien el CheckboxInput por defecto con form-control,
        # así que se puede ajustar aquí o en la plantilla.
        # Para 'en_reparacion', la clase 'form-check-input' es más apropiada.

from .models import Personal, Instalacion, CentroCosto

class PersonalForm(forms.ModelForm):
    instalacion_trabajo = forms.ModelChoiceField(
        queryset=Instalacion.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label="Instalación de Trabajo"
    )
    centro_costo = forms.ModelChoiceField(
        queryset=CentroCosto.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label="Centro de Costo"
    )
    
    def clean_rut(self):
        rut = self.cleaned_data.get('rut', '').strip()
        return validar_rut(rut)
    
    def clean_telefono_contacto(self):
        telefono = self.cleaned_data.get('telefono_contacto', '').strip()
        if not telefono.isdigit():
            raise ValidationError(_('El teléfono debe contener solo números.'))
        if len(telefono) < 8 or len(telefono) > 15:
            raise ValidationError(_('El teléfono debe tener entre 8 y 15 dígitos.'))
        return telefono

    class Meta:
        model = Personal
        fields = [
            'nombre', 'apellido', 'rut', 'fecha_nacimiento', 'direccion',
            'telefono_contacto', 'acepta_mensajeria_whatsapp',
            'instalacion_trabajo', 'centro_costo', 'legajo', 'fecha_ingreso',
            'usuario' # Si también se gestiona el usuario del sistema desde aquí
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_contacto': forms.TextInput(attrs={'class': 'form-control'}),
            'acepta_mensajeria_whatsapp': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'legajo': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_ingreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'usuario': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'acepta_mensajeria_whatsapp': 'Acepta Mensajería WhatsApp',
            'instalacion_trabajo': 'Instalación de Trabajo',
            'centro_costo': 'Centro de Costo',
            'fecha_ingreso': 'Fecha de Ingreso',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Opcional: si el campo usuario no es obligatorio
        if 'usuario' in self.fields: # Asegurarse que el campo existe
            self.fields['usuario'].required = False

class FileUploadForm(forms.Form):
    file = forms.FileField(label="Seleccionar archivo CSV o Excel")
