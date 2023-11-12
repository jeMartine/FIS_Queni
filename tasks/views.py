from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
from django.db import IntegrityError
from .forms import CrearGastoForm, IngresarIngresosForm
from .models import CrearGasto, IngresarIngresos
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.db.models import Sum
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from django.template.loader import get_template
from xhtml2pdf import pisa
import random
import io
from django.http import JsonResponse
import matplotlib.pyplot as plt
from io import BytesIO
from django.template.loader import get_template
from django.utils.timezone import make_aware
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from .models import Grupo, GastoCompartido
from .forms import GrupoForm, GastoCompartidoForm
from decimal import Decimal
from django.http import FileResponse
from reportlab.pdfgen import canvas
from django.core.mail import send_mail



# Create your views here.
def home(request):
    return render(request, 'signup.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Iniciar sesión al usuario
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'signup.html', {'form': form})
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})



@login_required 
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
     if request.method=='GET':
          return render(request, 'signin.html', {
               'form': AuthenticationForm
          })
     else:
          user = authenticate(request, username=request.POST['username'], password=request.POST
                       ['password'])
          if user is None:
            return render(request, 'signin.html',{
               'form': AuthenticationForm,
               'error': 'El usuario o la contraseña son incorrectos'
          })   
          else:
              login(request, user)
              return redirect('verGastos')
        
@login_required 
def verGastos(request):
    gastos = CrearGasto.objects.filter(user=request.user, datecompleted__isnull=True ) 
    
    return render(request, 'verGastos.html',{'Gastos' : gastos})

@login_required 
def verGastosCompletados(request):
    gastos = CrearGasto.objects.filter(user=request.user, datecompleted__isnull=False).order_by
    ('-datecompleted') 
    
    return render(request, 'verGastos.html',{'Gastos' : gastos})

def crearGastos(request):
    if request.method == 'GET':
        id_aleatorio = random.randint(10000, 99999)
        form = CrearGastoForm(initial={'id': id_aleatorio})

        fecha_actual = timezone.now()
        return render(request, 'crearGastos.html', {'form': form, 'fecha_actual': fecha_actual})
    else:
        form = CrearGastoForm(request.POST)
        if form.is_valid():
            new_gasto = form.save(commit=False)
            new_gasto.user = request.user
            new_gasto.save()
            return redirect('verGastos')
        else:
            return render(request, 'crearGastos.html', {
                'form': form,
                'error': 'Ingresa datos válidos'
            })
        
@login_required         
def gastoDetail(request, gasto_id):

    if request.method == 'GET':
        crearGasto = get_object_or_404(CrearGasto, pk=gasto_id, user = request.user)
        form = CrearGastoForm(instance = crearGasto)
        return render(request, 'gastoDetail.html' , {'gasto' : crearGasto, 'form' : form})
    else:
        try:
            crearGasto = get_object_or_404 (CrearGasto, pk = gasto_id)
            form = CrearGastoForm(request.POST, instance = crearGasto)
            form.save()
            return redirect('verGastos')
        except ValueError:
            return render(request, 'gastoDetail.html' , {'gasto' : crearGasto, 'form' : form, 
            'error' : "Error actualizando el gasto"})

@login_required 
def completeGasto(request, gasto_id):
    crearGastos = get_object_or_404(CrearGasto, pk = gasto_id, user = request.user)
    if request.method == 'POST':
        crearGastos.datecompleted = timezone.now()
        crearGastos.save()
        return redirect('verGastos')
    
@login_required 
def deleteGasto(request, gasto_id):
    crearGastos = get_object_or_404(CrearGasto, pk = gasto_id, user = request.user)
    if request.method == 'POST':
        crearGastos.delete()
        return redirect('verGastos')
    

@login_required 
def ingresarIngresos(request):
    if request.method == 'GET':
        return render(request, 'ingresarIngresos.html', {'form': IngresarIngresosForm})
    else:
        try:
            form = IngresarIngresosForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user 
            new_task.save()
            return redirect(reverse('verIngresos')) 
        except ValueError:
            return render(request, 'ingresarIngresos.html', {
                'form': IngresarIngresosForm,
                'error': 'Ingresa datos válidos'}
            )

@login_required 
def verIngresos(request):
    if request.method == 'GET':
        # Obtenemos el mes y año actual
        now = datetime.now()
        year = now.year
        month = now.month
        
        # Definimos la fecha de inicio y fin del mes actual
        first_day = datetime(year, month, 1)
        last_day = first_day + timedelta(days=30)
        
        # Filtramos los ingresos por usuario y fecha
        ingresos = IngresarIngresos.objects.filter(user=request.user, FechaDeRegistro__range=[first_day, last_day])
        
        return render(request, 'verIngresos.html', {'Ingresos': ingresos})
@login_required         
def ingresoDetail(request, ingreso_id):
    ingresarIngresos = get_object_or_404(IngresarIngresos, pk=ingreso_id, user=request.user)
    
    if request.method == 'GET':
        form = IngresarIngresosForm(instance=ingresarIngresos)
        return render(request, 'ingresoDetail.html', {'ingreso': ingresarIngresos, 'form': form})
    else:
        form = IngresarIngresosForm(request.POST, instance=ingresarIngresos)
        if form.is_valid():
            form.save()
            return redirect('verIngresos')  # Redirige a la lista de ingresos después de actualizar
        else:
            return render(request, 'ingresoDetail.html', {'ingreso': ingresarIngresos, 'form': form, 
                                                         'error': "Error al actualizar el ingreso. Por favor, verifica los datos."})

@login_required 
def deleteIngreso(request, ingreso_id):
    ingresarIngresos = get_object_or_404(IngresarIngresos, pk=ingreso_id, user=request.user)
    if request.method == 'POST':
        ingresarIngresos.delete()
        return redirect('verIngresos')
    
@login_required
def verBalance(request):
    template_path = 'verBalance_pdf.html'
    context = {
        'request': request,
    }
    
    if request.method == 'POST':
        fecha_inicio = request.POST['fecha_inicio']
        fecha_fin = request.POST['fecha_fin']
        
        gastos = CrearGasto.objects.filter(user=request.user, datecompleted__isnull=True, datecreated__gte=fecha_inicio, datecreated__lte=fecha_fin)
        ingresos = IngresarIngresos.objects.filter(user=request.user, FechaDeRegistro__gte=fecha_inicio, FechaDeRegistro__lte=fecha_fin)
        
        total_gastos = gastos.aggregate(Sum('Valor'))['Valor__sum']
        total_ingresos = ingresos.aggregate(Sum('Cantidad'))['Cantidad__sum']
        
        if total_gastos is None:
            total_gastos = 0
        
        if total_ingresos is None:
            total_ingresos = 0
        
        balance = total_ingresos - total_gastos
        
        context.update({
            'gastos': gastos,
            'ingresos': ingresos,
            'total_gastos': total_gastos,
            'total_ingresos': total_ingresos,
            'balance': balance,
        })
        
        # Generar el PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="balance_report.pdf"'
        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)
        
        if pisa_status.err:
            return HttpResponse('Error al generar el PDF', status=500)
        
        return response
    
    return render(request, 'verBalance.html')

@login_required
def verBalance_pdf(request):
    if request.method == 'POST':
        fecha_inicio = request.POST['fecha_inicio']
        fecha_fin = request.POST['fecha_fin']
        
        gastos = CrearGasto.objects.filter(user=request.user, datecompleted__isnull=True, datecreated__gte=fecha_inicio, datecreated__lte=fecha_fin)
        ingresos = IngresarIngresos.objects.filter(user=request.user, FechaDeRegistro__gte=fecha_inicio, FechaDeRegistro__lte=fecha_fin)
        
        total_gastos = gastos.aggregate(Sum('Valor'))['Valor__sum']
        total_ingresos = ingresos.aggregate(Sum('Cantidad'))['Cantidad__sum']
        
        if total_gastos is None:
            total_gastos = 0
        
        if total_ingresos is None:
            total_ingresos = 0

        balance = total_ingresos - total_gastos

        if balance > 0:
            consejos = "¡Felicidades! Tu balance es positivo. Considera ahorrar e invertir una parte del excedente."
        elif balance < 0:
            consejos = "Tu balance es negativo. Revisa tus gastos y crea un plan para mejorar tu situación financiera."
        else:
            consejos = "Tu balance es neutral. Sigue gestionando tus ingresos y gastos de manera responsable."

        context = {
            'request': request,
            'gastos': gastos,
            'ingresos': ingresos,
            'total_gastos': total_gastos,
            'total_ingresos': total_ingresos,
            'balance': balance,
            'consejos': consejos,
        }

        # Generar el PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="balance_report.pdf"'
        template_path = 'verBalance_pdf.html'
        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)

        if pisa_status.err:
            return HttpResponse('Error al generar el PDF', status=500)

        return response

@login_required
def estadisticas(request):
    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        start_date = make_aware(datetime.strptime(start_date_str, '%Y-%m-%d'))
        end_date = make_aware(datetime.strptime(end_date_str, '%Y-%m-%d'))

        usuario = request.user

        # Calcular ingresos y gastos en el rango de fechas
        ingresos = IngresarIngresos.objects.filter(user=usuario, FechaDeRegistro__range=(start_date, end_date)).aggregate(Sum('Cantidad'))
        gastos = CrearGasto.objects.filter(user=usuario, datecreated__range=(start_date, end_date)).aggregate(Sum('Valor'))

        # Calcular saldo (ingresos - gastos)
        saldo = ingresos['Cantidad__sum'] - gastos['Valor__sum']

        return render(request, 'estadisticas.html', {'ingresos': ingresos, 'gastos': gastos, 'saldo': saldo})
    else:
        return render(request, 'seleccionar_fechas.html')

def lista_grupos(request):
    grupos = Grupo.objects.all()
    user = request.user  # Obtén el usuario actual
    grupos_del_usuario = user.grupos_miembro.all()
    return render(request, 'lista_grupos.html', {'grupos': grupos, 'grupos_del_usuario': grupos_del_usuario})


@login_required
def crear_grupo(request):
    if request.method == 'POST':
        form = GrupoForm(request.POST)
        if form.is_valid():
            grupo = form.save(commit=False)
            grupo.creador = request.user
            grupo.save()
            grupo.miembros.add(request.user)
            return redirect('lista_grupos')
    else:
        form = GrupoForm()
    return render(request, 'crear_grupo.html', {'form': form})

@login_required
def unirse_grupo(request, grupo_id):
    grupo = Grupo.objects.get(pk=grupo_id)
    if request.user not in grupo.miembros.all():
        grupo.miembros.add(request.user)
        messages.success(request, f'Te has unido al grupo {grupo.nombre}.')
    return redirect('lista_grupos')

@login_required
def crear_gasto_compartido(request, grupo_id):
    grupo = get_object_or_404(Grupo, pk=grupo_id)

    if request.method == 'POST':
        form = GastoCompartidoForm(request.POST)
        if form.is_valid():
            gasto_compartido = form.save(commit=False)
            gasto_compartido.grupo = grupo
            gasto_compartido.save()

            # Agrega lógica para calcular las deudas y créditos de los miembros del grupo aquí
            # Puedes acceder a los miembros del grupo con grupo.miembros.all() y
            # realizar los cálculos según tus reglas de negocio.
            
            # Redirige a la lista de grupos una vez que se ha creado el gasto compartido
            return redirect('lista_grupos')
    else:
        form = GastoCompartidoForm()
    
    return render(request, 'crear_gasto_compartido.html', {'form': form, 'grupo': grupo})

@login_required
def ver_grupo(request, grupo_id):
    grupo = Grupo.objects.get(pk=grupo_id)
    
    # Obtener los miembros del grupo
    miembros = grupo.miembros.all()

    gastos = GastoCompartido.objects.filter(grupo=grupo)

    # Calcular el total de ingresos del grupo
    total_ingresos = float(miembros.aggregate(Sum('ingresaringresos__Cantidad'))['ingresaringresos__Cantidad__sum'] or 0.0)

    # Calcular el total de montos de gastos compartidos
    total_monto_gastos = float(gastos.aggregate(Sum('monto'))['monto__sum'] or 0.0)

    # Calcular los aportes individuales
    aportes = {}
    for miembro in miembros:
        ingresos_miembro = float(miembro.ingresaringresos_set.aggregate(Sum('Cantidad'))['Cantidad__sum'] or 0.0)
        if ingresos_miembro:
            aporte_individual = (ingresos_miembro / total_ingresos) * total_monto_gastos
            aportes[miembro.username] = aporte_individual

    return render(request, 'ver_grupo.html', {'grupo': grupo, 'miembros': miembros, 'aportes': aportes, 'gastos': gastos})

def generate_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sample.pdf"'

    # Crear un objeto PDF con ReportLab
    p = canvas.Canvas(response)
    p.drawString(100, 750, "¡Hola, este es un PDF de muestra!")
    p.showPage()
    p.save()

    return response

def send_email_with_attachment(request):
    subject = 'Asunto del correo'
    message = 'Cuerpo del correo.'
    from_email = 'tu_correo@gmail.com'
    recipient_list = ['destinatario@example.com']

    # Adjunta el archivo PDF generado en el paso 3
    pdf_file = open('sample.pdf', 'rb')

    send_mail(subject, message, from_email, recipient_list, fail_silently=False, attachment=pdf_file)

    return HttpResponse('Correo enviado con éxito.')


