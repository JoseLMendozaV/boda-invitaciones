from __future__ import annotations


from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from .models import ConfiguracionBoda
import logging

import re
from urllib.parse import quote_plus

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
            'invitacion_url': invitacion.id,
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

### Enviar al telefono

def to_wa_me_number(raw_phone: str, default_country="507") -> str | None:
    # Solo dígitos con código de país, sin '+'
    if not raw_phone:
        return None
    digits = re.sub(r"\D", "", raw_phone)
    if not digits:
        return None
    if digits.startswith("00"):
        digits = digits[2:]
    # si ya viene con +507, digits ya está sin '+'
    if digits.startswith(default_country):
        return digits
    # asume país por defecto
    return f"{default_country}{digits}"

def wa_share_link(phone_wa: str, text: str) -> str:
    return f"https://wa.me/{phone_wa}?text={quote_plus(text or '')}"