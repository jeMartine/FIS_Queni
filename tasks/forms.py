from django import forms
from django.forms import ModelForm
from .models import CrearGasto
from .models import IngresarIngresos
from .models import Grupo
from .models import GastoCompartido
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label= 'Email')
    first_name = forms.CharField(label= 'Nombre')
    last_name = forms.CharField(label= 'Apellido')
    password1 = forms.CharField(label= 'Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirma contraseña', widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username','first_name', 'last_name' , 'email', 'password1', 'password2']
        help_texts = {k:"" for k in fields}


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