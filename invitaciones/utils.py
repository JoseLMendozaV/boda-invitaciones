# -*- coding: utf-8 -*-
from django.core.mail import EmailMultiAlternatives
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
    Envía un email con la invitación de boda usando UTF-8
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
        
        # Subject con acentos y caracteres especiales
        subject = f'¡Estás invitado/a a la boda de {boda.nombre_novia} y {boda.nombre_novio}!'
        
        # URL para ver la invitación
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        invitacion_url = f"{site_url}/invitacion/{invitacion.codigo_qr}/"
        
        # Contexto para el template
        context = {
            'invitacion': invitacion,
            'invitacion_url': invitacion.id,
            'boda': boda,
        }
        
        # Renderizar templates
        html_message = render_to_string('emails/invitacion_email.html', context)
        plain_message = strip_tags(html_message)
        
        # ¡CLAVE! Usar EmailMultiAlternatives en lugar de send_mail
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[invitacion.email]
        )
        
        # Configurar UTF-8 explícitamente
        msg.encoding = 'utf-8'
        msg.attach_alternative(html_message, "text/html")
        
        # Enviar
        msg.send()
        
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
            
        subject = f'Confirmacion de respuesta - Boda de {boda.nombre_novia} y {boda.nombre_novio}'
        
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

def obtener_estadisticas_invitaciones():
    """
    Función auxiliar para obtener estadísticas de invitaciones
    """
    from .models import Invitacion
    
    total = Invitacion.objects.count()
    respondidas = Invitacion.objects.filter(ha_respondido=True).count()
    asistiran = Invitacion.objects.filter(asistira=True).count()
    no_asistiran = Invitacion.objects.filter(asistira=False).count()
    pendientes = total - respondidas
    
    return {
        'total': total,
        'respondidas': respondidas,
        'asistiran': asistiran,
        'no_asistiran': no_asistiran,
        'pendientes': pendientes,
        'porcentaje_respuesta': round((respondidas / total * 100) if total > 0 else 0, 1)
    }