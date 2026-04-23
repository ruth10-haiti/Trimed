#!/usr/bin/env python
import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trimed_backend.settings')
django.setup()

User = get_user_model()

if not User.objects.filter(email='admin@trimedh.com').exists():
    User.objects.create_superuser(
        email='admin@trimedh.com',
        password='admin123',
        nom='Admin',
        prenom='System'
    )
    print("Superuser created successfully!")
else:
    print("Superuser already exists!")