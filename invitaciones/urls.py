from django.urls import path
from . import views

urlpatterns = [
    # Página principal/dashboard
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Gestión de invitaciones - USANDO UUID en lugar de int
    path('crear/', views.crear_invitacion, name='crear_invitacion'),
    path('ver/<uuid:invitacion_id>/', views.ver_invitacion, name='ver_invitacion'),
    
    # URLs públicas para invitados
    path('invitacion/<str:codigo_qr>/', views.carta_invitacion, name='carta_invitacion'),
    path('responder/<str:codigo_qr>/', views.responder_invitacion, name='responder_invitacion'),
    
    # Verificación de QR - USANDO UUID
    path('verificar/<str:qr_code>/', views.verificar_qr, name='verificar_qr'),
    path('mostrar-qr/<int:invitacion_id>/', views.mostrar_qr, name='mostrar_qr'),
    
    # Funcionalidades de email - USANDO UUID
    path('reenviar/<uuid:invitacion_id>/', views.reenviar_invitacion_ajax, name='reenviar_invitacion_ajax'),
    path('enviar-recordatorios/', views.enviar_recordatorios, name='enviar_recordatorios'),
    path('enviar-emails-masivos/', views.enviar_emails_masivos, name='enviar_emails_masivos'),
    path('enviar-emails-seleccionados/', views.enviar_emails_seleccionados, name='enviar_emails_seleccionados'),
    path('enviar-recordatorios-seleccionados/', views.enviar_recordatorios_seleccionados, name='enviar_recordatorios_seleccionados'),
    
    # APIs
    path('dashboard/estadisticas/', views.dashboard_estadisticas, name='dashboard_estadisticas'),
    
    # Exportar datos
    path('exportar-csv/', views.exportar_csv, name='exportar_csv'),
]