from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models.signals import post_save
from django.dispatch import receiver

class CrearGasto(models.Model):
    # Campo ID autogenerado por Django
    id = models.AutoField(primary_key=True)

    Nombre = models.CharField(max_length=50)
    
    TIPO_GASTO_CHOICES = [
        ('servicios', 'Servicio'),
        ('deuda', 'Deuda'),
        ('comida', 'Comida'),
        ('hogar', 'Hogar'),
        ('educacion','Educacion'),
        ('ocio','Ocio'),
        ('otros', 'Otros'),
    ]
    TipoGasto = models.CharField(max_length=50, choices=TIPO_GASTO_CHOICES)
    Descripcion = models.TextField(blank=True)
    Valor = models.BigIntegerField(default=0, blank=True, null=True)
    datecreated = models.DateTimeField(auto_now_add=True)
    datecompleted = models.DateTimeField(null=True)
    IMPORTANCIA_CHOICES = [
        ('alto', 'Alto'),
        ('medio', 'Medio'),
        ('bajo', 'Bajo'),
    ]
    Importancia = models.CharField(max_length=50, choices=IMPORTANCIA_CHOICES, default='medio')
    # Campo para la frecuencia de gasto periódico
    FRECUENCIA_CHOICES = [
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('unico', 'Único'),
    ]
    Frecuencia = models.CharField(max_length=50, choices=FRECUENCIA_CHOICES, default='unico')

     # Nuevo campo para la fecha de vencimiento
    FechaVencimiento = models.DateField(null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.Nombre + ' creado por: ' + self.user.username

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)


class IngresarIngresos(models.Model):
    Nombre = models.CharField(max_length=50)
    Cantidad = models.BigIntegerField(default=0, blank=True, null=True)
    FechaDeRegistro = models.DateTimeField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Grupo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    creador = models.ForeignKey(User, on_delete=models.CASCADE)
    miembros = models.ManyToManyField(User, related_name='grupos_miembro')

    def __str__(self):
        return self.nombre
    
class GastoCompartido(models.Model):
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()
    fecha = models.DateField()

    def __str__(self):
        return self.descripcion