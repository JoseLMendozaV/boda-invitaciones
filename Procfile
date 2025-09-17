web: python manage.py migrate && python manage.py collectstatic --noinput --clear && gunicorn boda_project.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120
