"""
WSGI config for attendance_app project.
"""

import os
from django.core.wsgi import get_wsgi_application

# Let Render / environment variables decide settings
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    os.environ.get("DJANGO_SETTINGS_MODULE", "attendance_app.settings")
)

application = get_wsgi_application()
