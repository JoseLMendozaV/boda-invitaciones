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
from .utils import enviar_invitacion_email, enviar_confirmacion_respuesta

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .utils import enviar_invitacion_email
import logging

logger = logging.getLogger(__name__)

#########################################



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
import json




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
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono', '')
        numero_invitados = int(request.POST.get('numero_invitados', 1))
        
        # Validaciones básicas
        if not nombre or not email:
            messages.error(request, 'El nombre y email son obligatorios')
            return render(request, 'crear_invitacion.html')
        
        try:
            # Crear la invitación
            invitacion = Invitacion.objects.create(
                nombre_invitado=nombre,
                email=email,
                telefono=telefono,
                numero_invitados=numero_invitados
            )
            
            # Intentar enviar el email
            email_enviado = enviar_invitacion_email(invitacion)
            
            if email_enviado:
                messages.success(
                    request, 
                    f'¡Invitación creada exitosamente! Se ha enviado por email a {email}'
                )
                logger.info(f'Invitación {invitacion.id} creada y email enviado a {email}')
            else:
                messages.warning(
                    request, 
                    f'Invitación creada, pero hubo un problema enviando el email a {email}. '
                    f'Puedes reenviarlo desde el dashboard.'
                )
                logger.warning(f'Invitación {invitacion.id} creada pero email falló para {email}')
            
            return redirect('ver_invitacion', invitacion_id=invitacion.id)
            
        except Exception as e:
            logger.error(f'Error creando invitación: {str(e)}')
            messages.error(request, f'Error al crear la invitación: {str(e)}')
            return render(request, 'crear_invitacion.html')
    
    return render(request, 'crear_invitacion.html')

def ver_invitacion(request, token):
    try:
        # Buscar por token QR o por ID
        invitacion = Invitacion.objects.get(qr_code=token)
    except Invitacion.DoesNotExist:
        try:
            # Intentar buscar por ID si el token es numérico
            invitacion = Invitacion.objects.get(id=int(token))
        except (Invitacion.DoesNotExist, ValueError):
            messages.error(request, 'Invitación no encontrada')
            return redirect('invitaciones:dashboard')
    
    configuracion = ConfiguracionBoda.objects.first()
    
    context = {
        'invitacion': invitacion,
        'configuracion': configuracion,
    }
    
    return render(request, 'ver_invitacion.html', context)

# Reemplaza tu vista responder_invitacion con esta versión corregida

def responder_invitacion(request, codigo_qr):  # ← Parámetro correcto: codigo_qr
    """Vista para que los invitados respondan a la invitación"""
    try:
        # Buscar la invitación por codigo_qr
        invitacion = Invitacion.objects.get(codigo_qr=codigo_qr)
    except Invitacion.DoesNotExist:
        messages.error(request, 'Invitación no encontrada.')
        return redirect('verificar_qr')  # o la URL que uses para verificar
    
    if request.method == 'POST':
        # Obtener los datos del formulario
        respuesta = request.POST.get('respuesta')  # 'aceptada' o 'rechazada'
        numero_acompanantes = int(request.POST.get('numero_acompanantes', 0))
        mensaje_personal = request.POST.get('mensaje_personal', '')
        
        # Actualizar la invitación
        if respuesta == 'aceptada':
            invitacion.estado = 'aceptada'
        elif respuesta == 'rechazada':
            invitacion.estado = 'rechazada'
        else:
            messages.error(request, 'Respuesta inválida')
            return render(request, 'responder_invitacion.html', {'invitacion': invitacion})
        
        # Si acepta, validar número de acompañantes
        if respuesta == 'aceptada':
            if numero_acompanantes > invitacion.numero_invitados - 1:  # -1 porque el titular cuenta
                messages.error(
                    request, 
                    f'No puedes traer más de {invitacion.numero_invitados - 1} acompañantes'
                )
                return render(request, 'responder_invitacion.html', {'invitacion': invitacion})
        
        # Guardar los cambios
        invitacion.fecha_respuesta = timezone.now()
        invitacion.save()
        
        # Enviar confirmación por email
        from .utils import enviar_confirmacion_respuesta
        if enviar_confirmacion_respuesta(invitacion):
            messages.success(
                request, 
                '¡Respuesta guardada! Te hemos enviado una confirmación por email.'
            )
        else:
            messages.success(request, 'Respuesta guardada correctamente.')
        
        # Redirigir a la carta de invitación o página de confirmación
        return redirect('carta_invitacion', codigo_qr=codigo_qr)
    
    # GET request - mostrar el formulario
    return render(request, 'responder_invitacion.html', {
        'invitacion': invitacion
    })

def mostrar_qr(request, invitacion_id):
    """Vista para mostrar el código QR de una invitación"""
    try:
        invitacion = Invitacion.objects.get(id=invitacion_id)
    except Invitacion.DoesNotExist:
        messages.error(request, 'Invitación no encontrada.')
        return redirect('dashboard')
    
    context = {
        'invitacion': invitacion,
    }
    
    return render(request, 'mostrar_qr.html', context)

@login_required
def verificar_qr(request):
    """Vista para verificar códigos QR - VERSION DEBUG"""
    print(f"DEBUG: Método de request: {request.method}")
    
    if request.method == 'POST':
        codigo_qr = request.POST.get('codigo_qr', '').strip()
        print(f"DEBUG: Código QR recibido: '{codigo_qr}'")
        
        if codigo_qr:
            try:
                invitacion = Invitacion.objects.get(codigo_qr=codigo_qr)
                print(f"DEBUG: Invitación encontrada para verificación: {invitacion.nombre_invitado}")
                
                # Marcar como verificado (llegó a la boda)
                invitacion.verificado = True
                invitacion.fecha_verificacion = timezone.now()
                invitacion.save()
                
                messages.success(
                    request, 
                    f'¡Bienvenido/a {invitacion.nombre_invitado}! Disfruta la celebración.'
                )
                return redirect('carta_invitacion', codigo_qr=codigo_qr)
                
            except Invitacion.DoesNotExist:
                print("DEBUG: Código QR no encontrado en verificación")
                messages.error(request, 'Código QR no válido o invitación no encontrada.')
        else:
            print("DEBUG: Código QR vacío")
            messages.error(request, 'Por favor ingresa un código QR válido.')
    
    # Listar todas las invitaciones para debug
    invitaciones = Invitacion.objects.all()
    print(f"DEBUG: Total de invitaciones en BD: {invitaciones.count()}")
    for inv in invitaciones:
        print(f"DEBUG: Invitación - ID: {inv.id}, Código QR: {inv.codigo_qr}, Nombre: {inv.nombre_invitado}")
    
    return render(request, 'verificar_qr.html', {'debug_invitaciones': invitaciones})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
import json

@login_required
def dashboard(request):
    """Vista del dashboard con estadísticas completas"""
    from .utils import obtener_estadisticas_invitaciones
    
    invitaciones = Invitacion.objects.all().order_by('-fecha_creacion')
    estadisticas = obtener_estadisticas_invitaciones()
    
    # Estadísticas de emails
    emails_enviados = Invitacion.objects.filter(email_enviado=True).count()
    invitaciones_sin_email = Invitacion.objects.filter(email_enviado=False).count()
    
    # Recordatorios pendientes (invitaciones sin respuesta por más de 7 días)
    fecha_limite = timezone.now() - timedelta(days=7)
    recordatorios_pendientes = Invitacion.objects.filter(
        estado='pendiente',  # Usar 'estado' en lugar de 'ha_respondido'
        fecha_creacion__lt=fecha_limite
    ).count()
    
    # Calcular porcentajes
    total = estadisticas['total']
    porcentaje_emails = round((emails_enviados / total * 100) if total > 0 else 0, 1)
    
    # Porcentaje de verificados sobre los que confirmaron asistencia
    aceptadas = estadisticas['asistiran']
    verificadas = Invitacion.objects.filter(verificado=True).count()
    porcentaje_verificadas = round((verificadas / aceptadas * 100) if aceptadas > 0 else 0, 1)
    
    context = {
        'invitaciones': invitaciones,
        'total_invitaciones': estadisticas['total'],
        'aceptadas': estadisticas['asistiran'],
        'pendientes': estadisticas['pendientes'],
        'verificadas': verificadas,
        'emails_enviados': emails_enviados,
        'porcentaje_confirmadas': estadisticas['porcentaje_respuesta'],
        'porcentaje_verificadas': porcentaje_verificadas,
        'porcentaje_emails': porcentaje_emails,
        'invitaciones_sin_email': invitaciones_sin_email,
        'recordatorios_pendientes': recordatorios_pendientes,
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



@login_required
@require_POST
def reenviar_invitacion_ajax(request, invitacion_id):
    """Vista AJAX para reenviar invitación"""
    try:
        invitacion = Invitacion.objects.get(id=invitacion_id)
        
        if enviar_invitacion_email(invitacion):
            # Marcar como email enviado
            invitacion.email_enviado = True
            invitacion.fecha_ultimo_email = timezone.now()
            invitacion.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Email reenviado a {invitacion.email}'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Error al enviar email'
            })
            
    except Invitacion.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Invitación no encontrada'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error inesperado: {str(e)}'
        })
    




@login_required
@require_POST
def enviar_recordatorios(request):
    """Enviar recordatorios a invitaciones pendientes"""
    # Buscar invitaciones pendientes de más de 7 días
    fecha_limite = timezone.now() - timedelta(days=7)
    invitaciones_pendientes = Invitacion.objects.filter(
        estado='pendiente',
        fecha_creacion__lt=fecha_limite
    )
    
    enviados = 0
    for invitacion in invitaciones_pendientes:
        if enviar_recordatorio_email(invitacion):
            enviados += 1
    
    return JsonResponse({
        'success': True,
        'enviados': enviados,
        'total': invitaciones_pendientes.count()
    })

@login_required
@require_POST
def enviar_emails_masivos(request):
    """Enviar emails a todas las invitaciones que no los han recibido"""
    invitaciones_sin_email = Invitacion.objects.filter(email_enviado=False)
    
    enviados = 0
    for invitacion in invitaciones_sin_email:
        if enviar_invitacion_email(invitacion):
            invitacion.email_enviado = True
            invitacion.fecha_ultimo_email = timezone.now()
            invitacion.save()
            enviados += 1
    
    return JsonResponse({
        'success': True,
        'enviados': enviados,
        'total': invitaciones_sin_email.count()
    })



@login_required
@require_POST
@csrf_exempt
def enviar_emails_seleccionados(request):
    """Enviar emails a invitaciones seleccionadas"""
    data = json.loads(request.body)
    invitaciones_ids = data.get('invitaciones', [])
    
    invitaciones = Invitacion.objects.filter(id__in=invitaciones_ids)
    
    enviados = 0
    for invitacion in invitaciones:
        if enviar_invitacion_email(invitacion):
            invitacion.email_enviado = True
            invitacion.fecha_ultimo_email = timezone.now()
            invitacion.save()
            enviados += 1
    
    return JsonResponse({
        'success': True,
        'enviados': enviados,
        'total': len(invitaciones_ids)
    })

@login_required
@require_POST
@csrf_exempt
def enviar_recordatorios_seleccionados(request):
    """Enviar recordatorios a invitaciones seleccionadas"""
    data = json.loads(request.body)
    invitaciones_ids = data.get('invitaciones', [])
    
    invitaciones = Invitacion.objects.filter(id__in=invitaciones_ids)
    
    enviados = 0
    for invitacion in invitaciones:
        if enviar_recordatorio_email(invitacion):
            enviados += 1
    
    return JsonResponse({
        'success': True,
        'enviados': enviados,
        'total': len(invitaciones_ids)
    })

@login_required
def dashboard_estadisticas(request):
    """API para actualizar estadísticas en tiempo real"""
    from .utils import obtener_estadisticas_invitaciones
    
    estadisticas = obtener_estadisticas_invitaciones()
    emails_enviados = Invitacion.objects.filter(email_enviado=True).count()
    verificadas = Invitacion.objects.filter(verificado=True).count()
    
    return JsonResponse({
        'total': estadisticas['total'],
        'aceptadas': estadisticas['asistiran'],
        'pendientes': estadisticas['pendientes'],
        'verificadas': verificadas,
        'emails_enviados': emails_enviados,
    })

def carta_invitacion(request, codigo_qr):
    """Vista para mostrar la carta de invitación - VERSION DEBUG"""
    print(f"DEBUG: Buscando invitación con codigo_qr: {codigo_qr}")
    
    try:
        invitacion = Invitacion.objects.get(codigo_qr=codigo_qr)
        print(f"DEBUG: Invitación encontrada: {invitacion.nombre_invitado}")
    except Invitacion.DoesNotExist:
        print("DEBUG: Invitación NO encontrada")
        messages.error(request, f'Invitación con código {codigo_qr} no encontrada.')
        return redirect('dashboard')
    except Exception as e:
        print(f"DEBUG: Error inesperado: {e}")
        messages.error(request, f'Error al buscar invitación: {str(e)}')
        return redirect('dashboard')
    
    # Obtener configuración de la boda
    try:
        from .models import ConfiguracionBoda
        boda = ConfiguracionBoda.objects.first()
        print(f"DEBUG: Configuración de boda: {boda}")
    except Exception as e:
        print(f"DEBUG: Error obteniendo configuración de boda: {e}")
        boda = None
    
    context = {
        'invitacion': invitacion,
        'boda': boda,
    }
    
    print(f"DEBUG: Contexto para template: {context}")
    
    return render(request, 'carta_invitacion.html', context)


def exportar_csv(request):
    """Vista para exportar invitaciones a CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="invitaciones_boda.csv"'
    
    writer = csv.writer(response)
    
    # Escribir encabezados
    writer.writerow([
        'Nombre',
        'Email', 
        'Teléfono',
        'Número de Invitados',
        'Estado',
        'Verificado',
        'Fecha Creación',
        'Fecha Respuesta'
    ])
    
    # Escribir datos
    for invitacion in Invitacion.objects.all():
        writer.writerow([
            invitacion.nombre_invitado,
            invitacion.email,
            invitacion.telefono or '',
            invitacion.numero_invitados,
            invitacion.estado,
            'Sí' if invitacion.verificado else 'No',
            invitacion.fecha_creacion.strftime('%d/%m/%Y %H:%M') if invitacion.fecha_creacion else '',
            invitacion.fecha_respuesta.strftime('%d/%m/%Y %H:%M') if invitacion.fecha_respuesta else '',
        ])
    
    return response

# Vista simple para testing
def test_invitacion(request):
    """Vista de prueba para verificar que todo funciona"""
    invitaciones = Invitacion.objects.all()
    
    context = {
        'invitaciones': invitaciones,
        'total': invitaciones.count()
    }
    
    return render(request, 'test_invitacion.html', context)