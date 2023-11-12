from django import forms
from django.forms import ModelForm
from .models import CrearGasto
from .models import IngresarIngresos
from .models import Grupo
from .models import GastoCompartido

class GrupoForm(forms.ModelForm):
    class Meta:
        model = Grupo
        fields = ['nombre', 'descripcion']

class CrearGastoForm(forms.ModelForm):
    # Agrega el campo de Frecuencia al formulario
    FRECUENCIA_CHOICES = [
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('unico', 'Único'),
    ]

    Frecuencia = forms.ChoiceField(choices=FRECUENCIA_CHOICES, required=True, label='Frecuencia')

    class Meta:
        model = CrearGasto
        fields = ['Nombre', 'TipoGasto', 'Descripcion', 'Valor', 'Importancia', 'Frecuencia', 'FechaVencimiento']
        widgets = {
            'FechaVencimiento': forms.DateInput(attrs={'type': 'date'}),  # Utiliza el widget DateInput
        }

class IngresarIngresosForm(forms.ModelForm):
    class Meta:
        model = IngresarIngresos
        fields = ['Nombre', 'Cantidad', 'FechaDeRegistro']
        widgets = {
            'FechaDeRegistro': forms.TextInput(attrs={'type': 'datetime-local'}),
        }
class GastoCompartidoForm(forms.ModelForm):
    class Meta:
        model = GastoCompartido
        fields = ['grupo', 'monto', 'descripcion', 'fecha']

        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),  # Utiliza el widget DateInput
        }