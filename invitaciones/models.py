from django.db import models
from django.utils import timezone
import uuid

class Invitacion(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_invitado = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True)
    numero_invitados = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    codigo_qr = models.CharField(max_length=100, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(blank=True, null=True)
    verificado = models.BooleanField(default=False)
    fecha_verificacion = models.DateTimeField(blank=True, null=True)
    
    # Nuevos campos para personalización
    ubicacion_nombre = models.CharField(max_length=200, default="Parroquia Sagrado Corazón de Jesús")
    ubicacion_direccion = models.CharField(max_length=300, default="Av. 9a Oeste, David, Provincia de Chiriquí 507")
    ubicacion_maps_url = models.URLField(blank=True, null=True, help_text="URL de Google Maps", default="https://maps.app.goo.gl/9WFuwUWAHRs3yUSs9")
    fecha_boda = models.DateField(default="2026-02-21")
    hora_boda = models.TimeField(default="18:00")
    
    def __str__(self):
        return f"{self.nombre_invitado} - {self.numero_invitados} invitados"
    
    class Meta:
        verbose_name = "Invitación"
        verbose_name_plural = "Invitaciones"

class ConfiguracionBoda(models.Model):
    """Configuración global para la boda"""
    nombre_novio = models.CharField(max_length=100, default="José")
    nombre_novia = models.CharField(max_length=100, default="Grace")
    
    # Información de padres
    padre_novio_1 = models.CharField(max_length=150, default="José Longino Mendoza Avilés")
    padre_novio_2 = models.CharField(max_length=150, default="Vanessa Vianeth Valdés Sánchez")
    padre_novia_1 = models.CharField(max_length=150, default="Gregorio Quirós Caballero")
    padre_novia_2 = models.CharField(max_length=150, default="Jeovana del Carmen Espinosa Montenegro")
    
    # Historia de amor
    historia_amor = models.TextField(default="""Hace dos años, éramos dos desconocidos cuyos caminos se cruzaron por el destino. 
    Desde aquella primera cita llena de risas y emociones, nuestra historia ha sido un viaje lleno de amor y sueños compartidos.""")
    
    # Fotos de preboda (URLs o rutas de archivos)
    foto_preboda_1 = models.URLField(blank=True, null=True, help_text="URL de la primera foto de preboda")
    foto_preboda_2 = models.URLField(blank=True, null=True, help_text="URL de la segunda foto de preboda")
    foto_preboda_3 = models.URLField(blank=True, null=True, help_text="URL de la tercera foto de preboda")
    
    # Configuración por defecto
    fecha_boda_default = models.DateField(default="2026-02-21")
    hora_boda_default = models.TimeField(default="18:00")
    ubicacion_default = models.CharField(max_length=200, default="Parroquia Sagrado Corazón de Jesús")
    direccion_default = models.CharField(max_length=300, default="Av. 9a Oeste, David, Provincia de Chiriquí 507")
    maps_url_default = models.URLField(blank=True, null=True, default="https://maps.app.goo.gl/9WFuwUWAHRs3yUSs9")
    
    class Meta:
        verbose_name = "Configuración de la Boda"
        verbose_name_plural = "Configuración de la Boda"
    
    def __str__(self):
        return f"Boda de {self.nombre_novio} y {self.nombre_novia}"
    
    def save(self, *args, **kwargs):
        # Asegurar que solo exista una configuración
        if not self.pk and ConfiguracionBoda.objects.exists():
            raise ValueError('Solo puede existir una configuración de boda')
        return super().save(*args, **kwargs)