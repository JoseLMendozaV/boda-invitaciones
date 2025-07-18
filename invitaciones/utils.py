from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from .models import ConfiguracionBoda
import logging

logger = logging.getLogger(__name__)

def enviar_invitacion_email(invitacion):
    """
    Envía un email con la invitación de boda
    """
    try:
        # Obtener la configuración de la boda (asumiendo que hay una)
        try:
            boda = ConfiguracionBoda.objects.first()
            if not boda:
                logger.error('No hay configuración de boda disponible')
                return False
        except:
            logger.error('Error obteniendo configuración de boda')
            return False
        
        # Datos de la invitación
        subject = f'¡Estás invitado/a a la boda de {boda.nombre_novia} y {boda.nombre_novio}!'
        
        # URL para ver la invitación (ajusta según tu estructura de URLs)
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        invitacion_url = f"{site_url}/invitacion/{invitacion.codigo_qr}/"
        
        # Contexto para el template
        context = {
            'invitacion': invitacion,
            'invitacion_url': invitacion_url,
            'boda': boda,
        }
        
        # Renderizar el template HTML
        html_message = render_to_string('emails/invitacion_email.html', context)
        plain_message = strip_tags(html_message)
        
        # Enviar el email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invitacion.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f'Email enviado exitosamente a {invitacion.email}')
        return True
        
    except Exception as e:
        logger.error(f'Error enviando email a {invitacion.email}: {str(e)}')
        return False

def enviar_confirmacion_respuesta(invitacion):
    """
    Envía confirmación cuando alguien responde a la invitación
    """
    try:
        # Obtener la configuración de la boda
        try:
            boda = ConfiguracionBoda.objects.first()
            if not boda:
                logger.error('No hay configuración de boda disponible')
                return False
        except:
            logger.error('Error obteniendo configuración de boda')
            return False
            
        subject = f'Confirmación de respuesta - Boda de {boda.nombre_novia} y {boda.nombre_novio}'
        
        context = {
            'invitacion': invitacion,
            'boda': boda,
        }
        
        html_message = render_to_string('emails/confirmacion_respuesta.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invitacion.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f'Confirmación enviada a {invitacion.email}')
        return True
        
    except Exception as e:
        logger.error(f'Error enviando confirmación a {invitacion.email}: {str(e)}')
        return False

def enviar_recordatorio_email(invitacion):
    """
    Envía un email de recordatorio para invitaciones pendientes
    """
    try:
        # Obtener la configuración de la boda
        try:
            boda = ConfiguracionBoda.objects.first()
            if not boda:
                logger.error('No hay configuración de boda disponible')
                return False
        except:
            logger.error('Error obteniendo configuración de boda')
            return False
        
        # Datos del recordatorio
        subject = f'Recordatorio: Tu respuesta para la boda de {boda.nombre_novia} y {boda.nombre_novio}'
        
        # URL para responder
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        responder_url = f"{site_url}/responder/{invitacion.codigo_qr}/"
        
        # Contexto para el template
        context = {
            'invitacion': invitacion,
            'responder_url': responder_url,
            'boda': boda,
        }
        
        # Renderizar el template HTML
        html_message = render_to_string('emails/recordatorio_email.html', context)
        plain_message = strip_tags(html_message)
        
        # Enviar el email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invitacion.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f'Recordatorio enviado exitosamente a {invitacion.email}')
        return True
        
    except Exception as e:
        logger.error(f'Error enviando recordatorio a {invitacion.email}: {str(e)}')
        return False

def obtener_estadisticas_invitaciones():
    """
    Función auxiliar para obtener estadísticas de invitaciones
    """
    from .models import Invitacion
    
    total = Invitacion.objects.count()
    
    # Usar 'estado' en lugar de 'ha_respondido'
    # Asumiendo que cuando estado != 'pendiente' significa que ha respondido
    respondidas = Invitacion.objects.exclude(estado='pendiente').count()
    
    # Contar por estado específico
    aceptadas = Invitacion.objects.filter(estado='aceptada').count()
    rechazadas = Invitacion.objects.filter(estado='rechazada').count()
    
    # Pendientes son las que tienen estado 'pendiente'
    pendientes = Invitacion.objects.filter(estado='pendiente').count()
    
    return {
        'total': total,
        'respondidas': respondidas,
        'asistiran': aceptadas,  # Los que confirmaron que van
        'no_asistiran': rechazadas,  # Los que confirmaron que no van
        'pendientes': pendientes,
        'porcentaje_respuesta': round((respondidas / total * 100) if total > 0 else 0, 1)
    }