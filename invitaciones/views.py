from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Invitacion, ConfiguracionBoda
import qrcode
from io import BytesIO
import base64
import hashlib


# Agregar estos imports para emails
from django.contrib import messages
from .utils import enviar_invitacion_email, enviar_confirmacion_respuesta,to_wa_me_number,wa_share_link


from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

import logging, os

from django.urls import reverse

logger = logging.getLogger(__name__)

#########################################

def generar_codigo_qr(invitacion_id):
    """Genera un código QR único para la invitación"""
    # Crear un hash único basado en el ID de la invitación
    hash_object = hashlib.sha256(str(invitacion_id).encode())
    return hash_object.hexdigest()[:16]

@login_required
def crear_invitacion(request):
    """Vista para crear una nueva invitación - Solo usuarios autenticados"""
    if request.method == 'POST':
        nombre = (request.POST.get('nombre') or '').strip()
        email = (request.POST.get('email') or '').strip()  # ahora opcional
        telefono = (request.POST.get('telefono') or '').strip()

        # convierte con seguridad; default=1 si viene vacío o inválido
        try:
            numero_invitados = int(request.POST.get('numero_invitados', 1))
            if numero_invitados < 1:
                numero_invitados = 1
        except (TypeError, ValueError):
            numero_invitados = 1

        # Validaciones básicas: solo nombre obligatorio
        if not nombre:
            messages.error(request, 'El nombre es obligatorio.')
            return render(request, 'crear_invitacion.html', {
                'prefill': {'nombre': nombre, 'email': email, 'telefono': telefono, 'numero_invitados': numero_invitados}
            })

        try:
            # Crear la invitación (email puede ir vacío)
            invitacion = Invitacion.objects.create(
                nombre_invitado=nombre,
                email=email or None,   # guarda NULL si viene vacío
                telefono=telefono,
                numero_invitados=numero_invitados
            )

            # Enviar email solo si fue proporcionado
            if email:
                try:
                    email_enviado = enviar_invitacion_email(invitacion)
                    if email_enviado:
                        messages.success(request, f'¡Invitación creada! Email enviado a {email}.')
                        logger.info(f'Invitación {invitacion.id} creada y email enviado a {email}')
                    else:
                        messages.warning(request, f'Invitación creada. No se pudo enviar el email a {email}. Puedes reintentar desde el dashboard.')
                        logger.warning(f'Invitación {invitacion.id} creada pero email falló para {email}')
                except Exception as mail_err:
                    messages.warning(request, f'Invitación creada. Error al enviar email: {mail_err}')
                    logger.exception(f'Error enviando email para invitación {invitacion.id}')
            else:
                messages.success(request, '¡Invitación creada! (Sin correo electrónico).')
                logger.info(f'Invitación {invitacion.id} creada sin email')

            # 👉 WhatsApp: si hay teléfono, abre WhatsApp con el mensaje listo
            
            if telefono:
                # Construye un enlace público absoluto (ajusta el nombre de URL si cambia)
                try:
                    link_publico = request.build_absolute_uri(
                        reverse('ver_invitacion_publica', args=[invitacion.id])
                    )
                except Exception:
                    # Fallback a la vista protegida si aún no tienes una pública
                    link_publico = request.build_absolute_uri(
                        reverse('ver_invitacion', kwargs={'invitacion_id': invitacion.id})
                    )

                cuerpo = (
                    f"¡Hola {invitacion.nombre_invitado}! 💍\n\n"
                    f"Te compartimos tu invitación y tu QR:\n{link_publico}\n\n"
                    f"Número de invitados: {invitacion.numero_invitados}\n"
                    f"¡Te esperamos! 💚"
                )

                phone_wa = to_wa_me_number(telefono, default_country="507")
                if phone_wa:
                    wa_link = wa_share_link(phone_wa, cuerpo)
                    return redirect(wa_link)  # Abre WhatsApp Web / App
                else:
                    messages.warning(request, 'Invitación creada, pero el teléfono no es válido para WhatsApp.')

            # Si no hay teléfono o no se pudo formatear, ir al detalle
            return redirect('ver_invitacion', invitacion_id=invitacion.id)



            

        except Exception as e:
            logger.exception(f'Error creando invitación: {e}')
            messages.error(request, f'Error al crear la invitación: {e}')
            return render(request, 'crear_invitacion.html', {
                'prefill': {'nombre': nombre, 'email': email, 'telefono': telefono, 'numero_invitados': numero_invitados}
            })

    return render(request, 'crear_invitacion.html')

def ver_invitacion(request, invitacion_id):
    """Vista para mostrar la carta de invitación - Pública para invitados"""
    invitacion = get_object_or_404(Invitacion, id=invitacion_id)
    
    # Obtener configuración global de la boda
    try:
        config_boda = ConfiguracionBoda.objects.first()
    except:
        config_boda = None
    
    return render(request, 'carta_invitacion.html', {
        'invitacion': invitacion,
        'config_boda': config_boda
    })

# Vista mejorada para responder invitación (opcional)
def responder_invitacion(request, invitacion_id):
    """Vista para que el invitado responda a la invitación - Pública"""
    invitacion = get_object_or_404(Invitacion, id=invitacion_id)
    
    if request.method == 'POST':
        respuesta = request.POST.get('respuesta')
        
        if respuesta in ['aceptada', 'rechazada']:
            invitacion.estado = respuesta
            invitacion.fecha_respuesta = timezone.now()
            
            if respuesta == 'aceptada':
                # Generar código QR solo si acepta
                invitacion.codigo_qr = generar_codigo_qr(invitacion.id)
            
            invitacion.save()
            messages.success(request, 'Respuesta enviada exitosamente')
            
            if respuesta == 'aceptada':
                return redirect('mostrar_qr', invitacion_id=invitacion.id)
        
        return redirect('ver_invitacion', invitacion_id=invitacion.id)
    
    return render(request, 'responder_invitacion.html', {'invitacion': invitacion})

def mostrar_qr(request, invitacion_id):
    """Vista para mostrar el código QR generado - Pública para invitados"""
    invitacion = get_object_or_404(Invitacion, id=invitacion_id, estado='aceptada')
    
    # Generar imagen QR
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(invitacion.codigo_qr)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir a base64 para mostrar en HTML
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return render(request, 'mostrar_qr.html', {
        'invitacion': invitacion,
        'qr_image': img_str
    })

@login_required
def verificar_qr(request):
    """Vista para verificar código QR en la boda - Solo usuarios autenticados"""
    if request.method == 'POST':
        codigo_qr = request.POST.get('codigo_qr')
        
        try:
            invitacion = Invitacion.objects.get(codigo_qr=codigo_qr, estado='aceptada')
            
            if invitacion.verificado:
                return JsonResponse({
                    'success': False,
                    'mensaje': 'Este código QR ya fue verificado anteriormente'
                })
            
            invitacion.verificado = True
            invitacion.fecha_verificacion = timezone.now()
            invitacion.save()
            
            return JsonResponse({
                'success': True,
                'mensaje': f'Bienvenido {invitacion.nombre_invitado}!',
                'invitado': invitacion.nombre_invitado,
                'numero_invitados': invitacion.numero_invitados
            })
            
        except Invitacion.DoesNotExist:
            return JsonResponse({
                'success': False,
                'mensaje': 'Código QR no válido'
            })
    
    return render(request, 'verificar_qr.html')

@login_required
def dashboard(request):
    """Dashboard para ver estadísticas de invitaciones - Solo usuarios autenticados"""
    
    # Estadísticas básicas
    total_invitaciones = Invitacion.objects.count()
    aceptadas = Invitacion.objects.filter(estado='aceptada').count()
    rechazadas = Invitacion.objects.filter(estado='rechazada').count()
    pendientes = Invitacion.objects.filter(estado='pendiente').count()
    verificadas = Invitacion.objects.filter(verificado=True).count()
    
    # Calcular porcentajes para las barras de progreso
    porcentaje_confirmadas = 0
    if total_invitaciones > 0:
        porcentaje_confirmadas = round((aceptadas / total_invitaciones) * 100, 1)
    
    porcentaje_verificadas = 0
    if aceptadas > 0:
        porcentaje_verificadas = round((verificadas / aceptadas) * 100, 1)
    
    # Calcular total de invitados (suma de numero_invitados de las aceptadas)
    total_invitados_confirmados = Invitacion.objects.filter(
        estado='aceptada'
    ).aggregate(
        total=models.Sum('numero_invitados')
    )['total'] or 0
    
    # Invitaciones ordenadas por fecha de creación (más recientes primero)
    invitaciones = Invitacion.objects.all().order_by('-fecha_creacion')
    
    context = {
        # Estadísticas básicas
        'total_invitaciones': total_invitaciones,
        'aceptadas': aceptadas,
        'rechazadas': rechazadas,
        'pendientes': pendientes,
        'verificadas': verificadas,
        
        # Porcentajes para las barras de progreso
        'porcentaje_confirmadas': porcentaje_confirmadas,
        'porcentaje_verificadas': porcentaje_verificadas,
        
        # Estadísticas adicionales
        'total_invitados_confirmados': total_invitados_confirmados,
        
        # Lista de invitaciones
        'invitaciones': invitaciones,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def exportar_invitados_csv(request):
    """Vista para exportar la lista de invitados en formato CSV - Solo usuarios autenticados"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="invitaciones_boda.csv"'
    
    # Agregar BOM para que Excel reconozca UTF-8
    response.write('\ufeff')
    
    writer = csv.writer(response)
    
    # Encabezados
    writer.writerow([
        'Nombre',
        'Email', 
        'Teléfono',
        'Número de Invitados',
        'Estado',
        'Verificado',
        'Fecha de Creación',
        'Fecha de Respuesta',
        'Fecha de Verificación'
    ])
    
    # Datos
    for invitacion in Invitacion.objects.all().order_by('nombre_invitado'):
        writer.writerow([
            invitacion.nombre_invitado,
            invitacion.email,
            invitacion.telefono or '',
            invitacion.numero_invitados,
            invitacion.get_estado_display(),
            'Sí' if invitacion.verificado else 'No',
            invitacion.fecha_creacion.strftime('%d/%m/%Y %H:%M') if invitacion.fecha_creacion else '',
            invitacion.fecha_respuesta.strftime('%d/%m/%Y %H:%M') if invitacion.fecha_respuesta else '',
            invitacion.fecha_verificacion.strftime('%d/%m/%Y %H:%M') if invitacion.fecha_verificacion else '',
        ])
    
    return response

# Vista adicional para login/logout (opcional)
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    """Vista personalizada para login"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bienvenido {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Credenciales inválidas')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

@login_required
def logout_view(request):
    """Vista para logout"""
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente')
    return redirect('login')




@login_required
def reenviar_invitacion(request, invitacion_id):
    """Vista para reenviar una invitación por email"""
    try:
        invitacion = Invitacion.objects.get(id=invitacion_id)
        
        if enviar_invitacion_email(invitacion):
            messages.success(request, f'Invitación reenviada exitosamente a {invitacion.email}')
            logger.info(f'Invitación {invitacion_id} reenviada a {invitacion.email}')
        else:
            messages.error(request, f'Error al reenviar la invitación a {invitacion.email}')
            logger.error(f'Error reenviando invitación {invitacion_id} a {invitacion.email}')
            
    except Invitacion.DoesNotExist:
        messages.error(request, 'Invitación no encontrada')
        logger.error(f'Intento de reenviar invitación inexistente: {invitacion_id}')
    except Exception as e:
        messages.error(request, f'Error inesperado: {str(e)}')
        logger.error(f'Error inesperado reenviando invitación {invitacion_id}: {str(e)}')
    
    return redirect('dashboard')  # o donde tengas tu lista de invitaciones