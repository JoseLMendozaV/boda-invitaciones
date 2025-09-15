from __future__ import annotations

from email.header import Header
from email.utils import formataddr
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from .models import ConfiguracionBoda
import logging

import re
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

def enviar_invitacion_email(invitacion) -> bool:
    if not invitacion.email:
        return False

    # Configuración de la boda
    boda = ConfiguracionBoda.objects.first()
    if not boda:
        logger.error('No hay configuración de boda disponible')
        return False

    # Link absoluto público (ajusta si tu ruta real es otra)
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000').rstrip('/')
    link_publico = f"{site_url}/invitacion/{invitacion.codigo_qr}/"

    # SUBJECT codificado en UTF-8
    subject_text = f"Invitación a la boda de {boda.nombre_novia} y {boda.nombre_novio}"
    subject = str(Header(subject_text, 'utf-8'))

    # FROM seguro: email puro o con nombre codificado aparte
    sender_email = settings.DEFAULT_FROM_EMAIL  # ej: "no-reply@tu-dominio.com"
    sender_name = getattr(settings, 'DEFAULT_FROM_NAME', '')  # opcional en settings.py
    if sender_name:
        from_email = formataddr((str(Header(sender_name, 'utf-8')), sender_email))
    else:
        from_email = sender_email

    # Cuerpo
    context = {'invitacion': invitacion, 'boda': boda, 'link_publico': link_publico}
    html_content = render_to_string('emails/invitacion_email.html', context)
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[invitacion.email],
    )
    msg.encoding = 'utf-8'  # ← clave para ñ/acentos/emoji en el cuerpo
    msg.attach_alternative(html_content, "text/html")
    sent = msg.send(fail_silently=False)
    logger.info(f'Email enviado a {invitacion.email} (sent={sent})')
    return sent > 0

def enviar_confirmacion_respuesta(invitacion) -> bool:
    if not invitacion.email:
        return False

    boda = ConfiguracionBoda.objects.first()
    if not boda:
        logger.error('No hay configuración de boda disponible')
        return False

    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000').rstrip('/')
    link_publico = f"{site_url}/invitacion/{invitacion.codigo_qr}/"

    subject_text = f"Confirmación de respuesta - Boda de {boda.nombre_novia} y {boda.nombre_novio}"
    subject = str(Header(subject_text, 'utf-8'))

    sender_email = settings.DEFAULT_FROM_EMAIL
    sender_name = getattr(settings, 'DEFAULT_FROM_NAME', '')
    from_email = formataddr((str(Header(sender_name, 'utf-8')), sender_email)) if sender_name else sender_email

    context = {'invitacion': invitacion, 'boda': boda, 'link_publico': link_publico}
    html_content = render_to_string('emails/confirmacion_respuesta.html', context)
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[invitacion.email],
    )
    msg.encoding = 'utf-8'
    msg.attach_alternative(html_content, "text/html")
    sent = msg.send(fail_silently=False)
    logger.info(f'Confirmación enviada a {invitacion.email} (sent={sent})')
    return sent > 0

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