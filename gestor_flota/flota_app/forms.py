from django import forms
from .models import Vehiculo

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
