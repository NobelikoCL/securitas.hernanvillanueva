from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from .models import Personal, Cliente, Cargo, Instalacion, GestorCliente, RequerimientosCliente


class InstalacionForm(forms.ModelForm):
    class Meta:
        model = Instalacion
        fields = ['nombre', 'cliente', 'gestor', 'direccion', 
                 'contacto_nombre', 'contacto_telefono', 'contacto_email', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'cliente': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'gestor': forms.Select(attrs={'class': 'form-select'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': True}),
            'contacto_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto_telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'contacto_email': 'Ingrese una dirección de correo electrónico válida.',
        }
    
    def clean_contacto_email(self):
        email = self.cleaned_data.get('contacto_email')
        if email:  # Solo validar si se proporciona un correo
            try:
                validate_email(email)
            except forms.ValidationError:
                raise forms.ValidationError(
                    'Por favor ingrese una dirección de correo electrónico válida.'
                )
        return email

    def __init__(self, *args, **kwargs):
        cliente_id = kwargs.pop('cliente_id', None)
        super().__init__(*args, **kwargs)
        
        # Si se proporciona un cliente_id, filtrar los gestores disponibles
        if cliente_id:
            self.fields['gestor'].queryset = GestorCliente.objects.filter(cliente_id=cliente_id)
        else:
            self.fields['gestor'].queryset = GestorCliente.objects.none()
            
        # Hacer el campo de gestor opcional
        self.fields['gestor'].required = False


class GestorClienteForm(forms.ModelForm):
    class Meta:
        model = GestorCliente
        fields = ['cliente', 'nombre', 'cargo', 'email', 'telefono', 'activo']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'activo': '¿Activo?'
        }
        help_texts = {
            'activo': 'Desmarque para desactivar este gestor sin eliminarlo del sistema.'
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:  # Solo validar si se proporciona un correo
            try:
                validate_email(email)
            except forms.ValidationError:
                raise forms.ValidationError(
                    'Por favor ingrese una dirección de correo electrónico válida.'
                )
        return email

class PersonalForm(forms.ModelForm):
    acepta_whatsapp = forms.BooleanField(
        label='Acepta mensajería WhatsApp',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        label='Cliente',
        required=True,
        help_text='Seleccione el cliente al que pertenece el personal',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    instalacion = forms.ModelChoiceField(
        queryset=Instalacion.objects.none(),
        label='Instalación',
        required=True,
        help_text='Seleccione la instalación asignada',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Personal
        fields = [
            'nombres', 'apellidos', 'rut', 'telefono', 'direccion', 
            'email', 'cargo', 'fecha_contratacion', 'activo', 'acepta_whatsapp',
            'cliente', 'instalacion'
        ]
        widgets = {
            'fecha_contratacion': forms.DateInput(
                attrs={
                    'type': 'date', 
                    'class': 'form-control',
                    'required': 'required'
                }
            ),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+56 9 1234 5678',
                'required': 'required'
            }),
            'rut': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '12.345.678-9',
                'required': 'required'
            }),
            'cargo': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'nombres': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
        }
        labels = {
            'nombres': 'Nombres *',
            'apellidos': 'Apellidos *',
            'rut': 'RUT *',
            'telefono': 'Teléfono *',
            'direccion': 'Dirección *',
            'email': 'Correo Electrónico',
            'cargo': 'Cargo *',
            'fecha_contratacion': 'Fecha de Contratación *',
            'activo': 'Activo',
            'cliente': 'Cliente *',
            'instalacion': 'Instalación *',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si ya hay un cliente seleccionado, cargamos sus instalaciones
        if 'cliente' in self.data:
            try:
                cliente_id = int(self.data.get('cliente'))
                self.fields['instalacion'].queryset = Instalacion.objects.filter(
                    cliente_id=cliente_id, activa=True
                ).order_by('nombre')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.instalacion_asignada:
            # Si estamos editando y ya hay una instalación asignada
            self.fields['instalacion'].queryset = Instalacion.objects.filter(
                cliente=self.instance.instalacion_asignada.cliente, activa=True
            ).order_by('nombre')
            self.fields['cliente'].initial = self.instance.instalacion_asignada.cliente
        else:
            # Si no hay cliente seleccionado, no mostramos instalaciones
            self.fields['instalacion'].queryset = Instalacion.objects.none()
        
        # Hacer que el campo de cargo sea requerido
        self.fields['cargo'].required = True
        self.fields['cargo'].queryset = Cargo.objects.all()
        
        # Añadir clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            if field_name not in ['acepta_whatsapp', 'activo']:
                field.widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Verificar que hay clientes registrados
        if not Cliente.objects.exists():
            raise ValidationError(
                'No hay clientes registrados. Por favor, registre al menos un cliente antes de agregar personal.'
            )
            
        return cleaned_data
    
    def save(self, commit=True):
        # Asignar la instalación al personal
        personal = super().save(commit=False)
        instalacion = self.cleaned_data.get('instalacion')
        if instalacion:
            personal.instalacion_asignada = instalacion
        
        if commit:
            personal.save()
        return personal


class RequerimientosInstalacionForm(forms.ModelForm):
    class Meta:
        model = RequerimientosCliente
        fields = [
            'sistema_turnos_4x4',
            'requiere_personal',
            'personal_requerido',
            'personal_por_turno',
            'requiere_vehiculos',
            'cantidad_vehiculos',
            'requisitos_especiales',
            'notas'
        ]
        widgets = {
            'sistema_turnos_4x4': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'data-bs-toggle': 'tooltip',
                'title': 'Sistema de turnos 4x4 (4 días trabajo / 4 días libres)'
            }),
            'requiere_personal': forms.CheckboxInput(attrs={
                'class': 'form-check-input toggle-personal',
                'data-bs-toggle': 'collapse',
                'data-bs-target': '.personal-fields',
                'aria-expanded': 'false',
                'aria-controls': 'personalFields'
            }),
            'personal_requerido': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1'
            }),
            'personal_por_turno': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'step': '1'
            }),
            'requiere_vehiculos': forms.CheckboxInput(attrs={
                'class': 'form-check-input toggle-vehiculos',
                'data-bs-toggle': 'collapse',
                'data-bs-target': '.vehiculo-fields',
                'aria-expanded': 'false',
                'aria-controls': 'vehiculoFields'
            }),
            'cantidad_vehiculos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1'
            }),
            'requisitos_especiales': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ej: Personal con curso de manejo de extintores, vehículos 4x4, etc.'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notas adicionales sobre los requerimientos...'
            })
        }
        labels = {
            'sistema_turnos_4x4': 'Usar sistema de turnos 4x4',
            'personal_requerido': 'Total de personal requerido',
            'personal_por_turno': 'Personal por turno',
            'cantidad_vehiculos': 'Vehículos requeridos',
            'requisitos_especiales': 'Requisitos especiales',
            'notas': 'Notas adicionales'
        }
        help_texts = {
            'personal_requerido': 'Número total de personas necesarias para cubrir toda la instalación',
            'personal_por_turno': 'Número de personas necesarias por turno',
            'cantidad_vehiculos': 'Número total de vehículos necesarios para la instalación',
            'requisitos_especiales': 'Especifique cualquier requisito especial para el personal o vehículos',
            'notas': 'Cualquier información adicional relevante para la planificación'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer valores por defecto si es un nuevo formulario
        if not self.instance.pk:
            self.initial.update({
                'sistema_turnos_4x4': True,
                'requiere_personal': True,
                'personal_requerido': 1,
                'personal_por_turno': 1,
                'requiere_vehiculos': False,
                'cantidad_vehiculos': 0
            })

    def clean(self):
        cleaned_data = super().clean()
        requiere_personal = cleaned_data.get('requiere_personal')
        requiere_vehiculos = cleaned_data.get('requiere_vehiculos')
        
        # Validar que si requiere personal, se especifique la cantidad
        if requiere_personal and not cleaned_data.get('personal_requerido'):
            self.add_error('personal_requerido', 'Debe especificar la cantidad de personal requerido')
        
        # Validar que si requiere vehículos, se especifique la cantidad
        if requiere_vehiculos and not cleaned_data.get('cantidad_vehiculos'):
            self.add_error('cantidad_vehiculos', 'Debe especificar la cantidad de vehículos requeridos')
        
        # Validar que el personal por turno no sea mayor que el personal total
        if (requiere_personal and 
            cleaned_data.get('personal_por_turno', 0) > 
            cleaned_data.get('personal_requerido', 0)):
            self.add_error('personal_por_turno', 
                         'El personal por turno no puede ser mayor que el personal total requerido')
        
        return cleaned_data
