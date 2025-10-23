from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('crear/', views.crear_invitacion, name='crear_invitacion'),
    path('invitacion/<uuid:invitacion_id>/', views.ver_invitacion, name='ver_invitacion'),
    path('responder/<uuid:invitacion_id>/', views.responder_invitacion, name='responder_invitacion'),
    path('qr/<uuid:invitacion_id>/', views.mostrar_qr, name='mostrar_qr'),
    path('verificar/', views.verificar_qr, name='verificar_qr'),
    
    # Nueva URL para exportar CSV
    path('exportar-csv/', views.exportar_invitados_csv, name='exportar_csv'),

    # Nueva URL para reenviar invitaciones
    path('reenviar/<int:invitacion_id>/', views.reenviar_invitacion, name='reenviar_invitacion'),

]