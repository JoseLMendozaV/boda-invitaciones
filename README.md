cat > README.md << 'EOF'
# 💒 Aplicación de Invitaciones de Boda

Una aplicación Django completa para gestionar invitaciones de boda con códigos QR, sistema de verificación y dashboard administrativo.

## 🌟 Características

- ✅ Crear invitaciones personalizadas
- ✅ Cartas de invitación elegantes con diseño responsive
- ✅ Sistema de respuesta (aceptar/rechazar)
- ✅ Generación automática de códigos QR
- ✅ Verificación de códigos QR en tiempo real
- ✅ Dashboard con estadísticas
- ✅ Panel administrativo completo
- ✅ Prevención de códigos duplicados

## 🚀 Instalación

### Prerrequisitos
- Python 3.8+
- pip

### Pasos de instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/TU_USUARIO/boda-invitaciones.git
   cd boda-invitaciones
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar base de datos**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Crear superusuario**
   ```bash
   python manage.py createsuperuser
   ```

6. **Ejecutar servidor**
   ```bash
   python manage.py runserver
   ```

7. **Abrir en navegador**
   - Aplicación: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

## 📱 Uso

### Para Administradores
1. Accede al dashboard principal
2. Crea nuevas invitaciones con "Nueva Invitación"
3. Comparte el enlace de cada invitación con los invitados
4. Monitorea respuestas en tiempo real
5. Usa "Verificar QR" el día de la boda

### Para Invitados
1. Recibe el enlace de invitación
2. Ve tu carta de invitación personalizada
3. Responde aceptando o rechazando
4. Si aceptas, recibe tu código QR único
5. Presenta el código QR el día de la boda

## 🛠️ Tecnologías

- **Backend:** Django 4.2+
- **Frontend:** Bootstrap 5, HTML5, CSS3, JavaScript
- **Base de datos:** SQLite (desarrollo) / PostgreSQL (producción)
- **QR:** qrcode library
- **Iconos:** Font Awesome

## 📂 Estructura del Proyecto

```
boda_invitaciones/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── boda_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── invitaciones/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── crear_invitacion.html
│   │   ├── carta_invitacion.html
│   │   ├── responder_invitacion.html
│   │   ├── mostrar_qr.html
│   │   └── verificar_qr.html
│   └── migrations/
└── db.sqlite3
```

## 🔧 Configuración de Producción

### Variables de Entorno
Crea un archivo `.env` con:
```env
SECRET_KEY=tu-clave-secreta-muy-larga
DEBUG=False
DATABASE_URL=postgres://usuario:password@host:puerto/database
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password
```

### Deployment en Heroku
```bash
# Instalar Heroku CLI y hacer login
heroku create tu-app-boda

# Configurar variables de entorno
heroku config:set SECRET_KEY="tu-clave-secreta"
heroku config:set DEBUG=False

# Deploy
git push heroku main

# Ejecutar migraciones
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 🐛 Reportar Bugs

Si encuentras un bug, por favor crea un issue con:
- Descripción del problema
- Pasos para reproducirlo
- Comportamiento esperado vs actual
- Screenshots (si aplica)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 Autor

**Tu Nombre**
- GitHub: [@JoseLMendozaV](https://https://github.com/JoseLMendozaV)
- Email: sagaka1g@gmail.com

## 🙏 Agradecimientos

- Django Team por el excelente framework
- Bootstrap por los componentes UI
- Font Awesome por los iconos
- qrcode library por la generación de códigos QR

---

⭐ Si este proyecto te ayudó, ¡dale una estrella!
EOF