import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

# Initialize Django
import django
django.setup()

# Import Django's WSGI handler
from django.core.wsgi import get_wsgi_application

# Get the WSGI application (must be top-level for Vercel)
app = get_wsgi_application()
