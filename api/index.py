import os
import sys
import traceback

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

try:
    # Initialize Django
    import django
    django.setup()

    # Import Django's WSGI handler
    from django.core.wsgi import get_wsgi_application

    # Get the WSGI application
    application = get_wsgi_application()
except Exception as e:
    # Log error for debugging
    print(f"Error initializing Django: {str(e)}")
    print(traceback.format_exc())
    raise
