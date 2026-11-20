"""Helper used only to reproduce the CORS error requested by the lab guide.

Run: python manage.py runserver 127.0.0.1:8002 --noreload --settings=config.settings_cors_error
The authorized React origin is deliberately removed here; the normal settings keep it.
"""
from .settings import *  # noqa: F401,F403

CORS_ALLOWED_ORIGINS = []
