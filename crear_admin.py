"""Script para crear superusuario automáticamente en el build de Render.

Ejecutar una sola vez al desplegar. Una vez creado el usuario, se puede
eliminar este archivo del repositorio.

Uso local:
    python crear_admin.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_prod')
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402

User = get_user_model()

USERNAME = 'admin'
EMAIL    = 'od.mendez0.2528@cbtis198.edu.mx'
PASSWORD = 'monckyodi20_k*'   # ⚠️ CAMBIA esta contraseña por una segura

if not User.objects.filter(username=USERNAME).exists():
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
    print(f'✅ Superusuario "{USERNAME}" creado exitosamente.')
else:
    print(f'ℹ️  Superusuario "{USERNAME}" ya existe. Nada que hacer.')