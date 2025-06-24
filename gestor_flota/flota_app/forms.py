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
        fields = ['patente', 'marca', 'modelo', 'año', 'kilometraje', 'en_reparacion', 'instalacion_base']
        widgets = {
            'patente': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'año': forms.NumberInput(attrs={'class': 'form-control'}),
            'kilometraje': forms.NumberInput(attrs={'class': 'form-control'}),
            'en_reparacion': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'instalacion_base': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'año': 'Año',
            'en_reparacion': 'En Reparación',
            'instalacion_base': 'Instalación Base',
        }

    def __init__(self, *args, **kwargs):
        self.cliente_obj = kwargs.pop('cliente_obj', None) # Para filtrar instalaciones por cliente
        super().__init__(*args, **kwargs)

        if 'instalacion_base' in self.fields:
            if self.cliente_obj:
                self.fields['instalacion_base'].queryset = Instalacion.objects.filter(centro_costo__cliente=self.cliente_obj).select_related('centro_costo')
            elif self.instance and self.instance.pk and self.instance.instalacion_base:
                # Si es una instancia existente y tiene instalacion_base, filtramos al cliente de esa instalacion
                self.fields['instalacion_base'].queryset = Instalacion.objects.filter(
                    centro_costo__cliente=self.instance.instalacion_base.centro_costo.cliente
                ).select_related('centro_costo')
            else:
                # Si no hay cliente_obj (ej. admin global), mostrar todas las instalaciones.
                # Podría ser muy largo, considerar otra UX para este caso.
                self.fields['instalacion_base'].queryset = Instalacion.objects.all().select_related('centro_costo')

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
        self.cliente_obj = kwargs.pop('cliente_obj', None) # Para filtrar instalaciones/CC por cliente
        super().__init__(*args, **kwargs)

        if self.cliente_obj:
            self.fields['instalacion_trabajo'].queryset = Instalacion.objects.filter(centro_costo__cliente=self.cliente_obj).select_related('centro_costo')
            self.fields['centro_costo'].queryset = CentroCosto.objects.filter(cliente=self.cliente_obj)
        else:
            # Si no hay cliente_obj (ej. admin global), mostrar todos.
            # Considerar la UX si hay muchos datos.
            self.fields['instalacion_trabajo'].queryset = Instalacion.objects.all().select_related('centro_costo')
            self.fields['centro_costo'].queryset = CentroCosto.objects.all()

        # Opcional: si el campo usuario no es obligatorio
        if 'usuario' in self.fields: # Asegurarse que el campo existe
            self.fields['usuario'].required = False

    def clean(self):
        cleaned_data = super().clean()
        instalacion = cleaned_data.get("instalacion_trabajo")
        centro_costo_manual = cleaned_data.get("centro_costo")

        if instalacion and centro_costo_manual:
            if instalacion.centro_costo != centro_costo_manual:
                self.add_error('instalacion_trabajo',
                               ValidationError(f"La instalación '{instalacion}' pertenece al centro de costo '{instalacion.centro_costo}'. Usted seleccionó '{centro_costo_manual}'.", code='inconsistent_cc'))
                self.add_error('centro_costo',
                               ValidationError(f"El centro de costo '{centro_costo_manual}' no coincide con el de la instalación '{instalacion.centro_costo}'.", code='inconsistent_cc'))
        elif instalacion and not centro_costo_manual:
            # Si se seleccionó instalación pero no CC, autocompletar CC
            cleaned_data['centro_costo'] = instalacion.centro_costo

        return cleaned_data

class FileUploadForm(forms.Form):
    file = forms.FileField(label="Seleccionar archivo CSV o Excel", widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

# Formularios para Cliente, CentroCosto, Instalacion

from .models import Cliente

class ClienteForm(forms.ModelForm):
    def clean_rut(self):
        rut = self.cleaned_data.get('rut', '').strip()
        return validar_rut(rut) # Reutilizamos la función de validación de RUT

    class Meta:
        model = Cliente
        fields = ['nombre', 'rut', 'direccion', 'telefono', 'email']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class CentroCostoForm(forms.ModelForm):
    # El campo cliente se asignará automáticamente en la vista si solo hay un cliente,
    # o se podría seleccionar si hubiera múltiples (no es el caso aquí).
    # Por ahora, lo excluimos del formulario o lo hacemos de solo lectura si es necesario.
    class Meta:
        model = CentroCosto
        fields = ['nombre', 'codigo', 'cliente']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'cliente': forms.Select(attrs={'class': 'form-select'}), # Ya no es readonly por defecto
        }

    def __init__(self, *args, **kwargs):
        # cliente_obj es un argumento esperado que pasarán las vistas Create y Update
        # para indicar el contexto del cliente.
        self.cliente_obj = kwargs.pop('cliente_obj', None)
        super().__init__(*args, **kwargs)

        if self.cliente_obj:
            self.fields['cliente'].initial = self.cliente_obj
            self.fields['cliente'].widget.attrs['disabled'] = True # Deshabilitar si el cliente se pasa (contexto fijo)
        elif self.instance and self.instance.pk and self.instance.cliente: # En UpdateView si no se pasó cliente_obj
             self.fields['cliente'].initial = self.instance.cliente
             self.fields['cliente'].widget.attrs['disabled'] = True
        else:
            # Para CreateView fuera de un contexto de cliente (ej. admin global de CCs)
            # Dejar el campo cliente seleccionable.
            self.fields['cliente'].queryset = Cliente.objects.all()
            self.fields['cliente'].widget.attrs.pop('disabled', None) # Asegurar que no esté deshabilitado

class InstalacionForm(forms.ModelForm):
    class Meta:
        model = Instalacion
        fields = ['nombre', 'direccion', 'descripcion', 'centro_costo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'centro_costo': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        # cliente_obj es un argumento esperado que pasarán las vistas Create y Update
        # para indicar el contexto del cliente y así filtrar los Centros de Costo.
        self.cliente_obj = kwargs.pop('cliente_obj', None)
        super().__init__(*args, **kwargs)

        if self.cliente_obj:
            self.fields['centro_costo'].queryset = CentroCosto.objects.filter(cliente=self.cliente_obj)
        elif self.instance and self.instance.pk and self.instance.centro_costo:
            # Si es una instancia existente (UpdateView) y tiene un CC,
            # filtramos los CCs al cliente de ese CC para mantener la consistencia.
            self.fields['centro_costo'].queryset = CentroCosto.objects.filter(cliente=self.instance.centro_costo.cliente)
        else:
            # Si no se proporciona cliente_obj (ej. un admin global de instalaciones),
            # o es una nueva instancia sin contexto de cliente, mostrar todos los CC.
            # Esto podría necesitar más lógica si se accede fuera del flujo cliente->cc->instalacion.
            self.fields['centro_costo'].queryset = CentroCosto.objects.all()

        # Si después de filtrar, el queryset está vacío y es una creación,
        # podríamos deshabilitar el campo o dar una opción "Crear nuevo CC".
        # Por ahora, si está vacío, el select estará vacío.
        if not self.fields['centro_costo'].queryset.exists():
            self.fields['centro_costo'].help_text = "No hay centros de costo disponibles para el cliente seleccionado."
            # Considerar deshabilitar si es una creación y no hay opciones.
            # if not self.instance or not self.instance.pk:
            #     self.fields['centro_costo'].widget.attrs['disabled'] = True
