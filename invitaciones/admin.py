from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Invitacion, ConfiguracionBoda

@admin.register(Invitacion)
class InvitacionAdmin(admin.ModelAdmin):
    list_display = ['nombre_invitado', 'numero_invitados', 'estado', 'verificado', 'fecha_creacion', 'acciones']
    list_filter = ['estado', 'verificado', 'fecha_creacion']
    search_fields = ['nombre_invitado', 'email']
    readonly_fields = ['id', 'codigo_qr', 'fecha_creacion', 'fecha_respuesta', 'fecha_verificacion']
    
    fieldsets = (
        ('Información del Invitado', {
            'fields': ('nombre_invitado', 'email', 'telefono', 'numero_invitados')
        }),
        ('Estado de la Invitación', {
            'fields': ('estado', 'codigo_qr', 'verificado')
        }),
        ('Personalización (opcional)', {
            'fields': ('ubicacion_nombre', 'ubicacion_direccion', 'ubicacion_maps_url', 'fecha_boda', 'hora_boda'),
            'classes': ('collapse',)
        }),
        ('Fechas del Sistema', {
            'fields': ('id', 'fecha_creacion', 'fecha_respuesta', 'fecha_verificacion'),
            'classes': ('collapse',)
        }),
    )
    
    def acciones(self, obj):
        """Columna personalizada con botones de acción"""
        delete_url = reverse('admin:{}_{}_delete'.format(
            obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        change_url = reverse('admin:{}_{}_change'.format(
            obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        
        return format_html(
            '<a class="button" href="{}">Editar</a> '
            '<a class="button" href="{}" onclick="return confirm(\'¿Estás seguro de que deseas eliminar esta invitación?\');" '
            'style="background-color: #dc3545; color: white; margin-left: 5px;">Eliminar</a>',
            change_url, delete_url
        )
    
    acciones.short_description = 'Acciones'
    acciones.allow_tags = True
    
    def has_delete_permission(self, request, obj=None):
        # Permitir eliminar invitaciones
        return True
    
    def has_change_permission(self, request, obj=None):
        # Asegurar permisos de modificación
        return True
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        # Forzar la inclusión de delete_selected si el usuario tiene permisos
        if self.has_delete_permission(request):
            from django.contrib.admin.actions import delete_selected
            actions['delete_selected'] = (delete_selected, 'delete_selected', delete_selected.short_description)
        return actions
    
    # Acción personalizada para eliminar múltiples invitaciones
    def eliminar_invitaciones(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} invitaciones eliminadas exitosamente.')
    
    eliminar_invitaciones.short_description = "Eliminar invitaciones seleccionadas"
    actions = ['eliminar_invitaciones']

@admin.register(ConfiguracionBoda)
class ConfiguracionBodaAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Información de los Novios', {
            'fields': ('nombre_novio', 'nombre_novia')
        }),
        ('Padres del Novio', {
            'fields': ('padre_novio_1', 'padre_novio_2')
        }),
        ('Padres de la Novia', {
            'fields': ('padre_novia_1', 'padre_novia_2')
        }),
        ('Historia de Amor', {
            'fields': ('historia_amor',)
        }),
        ('Fotos de Preboda', {
            'fields': ('foto_preboda_1', 'foto_preboda_2', 'foto_preboda_3'),
            'description': 'URLs de las fotos de preboda (opcional)'
        }),
        ('Configuración por Defecto', {
            'fields': ('fecha_boda_default', 'hora_boda_default', 'ubicacion_default', 'direccion_default', 'maps_url_default')
        }),
    )
    
    def has_add_permission(self, request):
        # Solo permitir una configuración
        return not ConfiguracionBoda.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar la configuración
        return False