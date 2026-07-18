# flake8: noqa: F405
"""Production settings: imports everything from base.py, then applies prod overrides."""

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa F401

# Note: it is recommended to use the "DEBUG" environment variable to override this value in base.py.
# A future release may remove it from here.
DEBUG = False

# Production requires a database via DATABASE_URL. For Vercel, we support PostgreSQL
# but can also use SQLite for smaller deployments if needed.
if "DATABASE_URL" in env:
    DATABASES = {"default": env.db("DATABASE_URL")}
else:
    # Fallback to SQLite for Vercel deployments without external database
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Serve static files directly from the app via WhiteNoise (no separate web server / CDN required).
# Insert the middleware immediately after SecurityMiddleware, per WhiteNoise's docs.
MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,
    "whitenoise.middleware.WhiteNoiseMiddleware",
)
# Compress static files at collectstatic time. We avoid the *Manifest* variant because assets
# referenced inside built CSS (fonts/images) can break under hashed-manifest storage.
STORAGES["staticfiles"]["BACKEND"] = "whitenoise.storage.CompressedStaticFilesStorage"

# fix ssl mixed content issues
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Django security checklist settings.
# More details here: https://docs.djangoproject.com/en/stable/howto/deployment/checklist/
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HTTP Strict Transport Security settings
# Without uncommenting the lines below, you will get security warnings when running ./manage.py check --deploy
# https://docs.djangoproject.com/en/stable/ref/middleware/#http-strict-transport-security

# # Increase this number once you're confident everything works https://stackoverflow.com/a/49168623/8207
# SECURE_HSTS_SECONDS = 60
# # Uncomment these two lines if you are sure that you don't host any subdomains over HTTP.
# # You will get security warnings if you don't do this.
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

USE_HTTPS_IN_ABSOLUTE_URLS = True

# If you don't want to use environment variables to set production hosts you can add them here
# ALLOWED_HOSTS = ["example.com"]

# Your email config goes here.
# see https://github.com/anymail/django-anymail for more details / examples
# To use mailgun, uncomment the lines below and make sure your key and domain
# are available in the environment.
# EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"

# ANYMAIL = {
#     "MAILGUN_API_KEY": env("MAILGUN_API_KEY", default=None),
#     "MAILGUN_SENDER_DOMAIN": env("MAILGUN_SENDER_DOMAIN", default=None),
# }

ADMINS = ["achinga.chris@gmail.com"]

# Override Vite settings for production - always use built assets
DJANGO_VITE = {
    "default": {
        "dev_mode": False,
        "dev_server_host": env("DJANGO_VITE_HOST", default="localhost"),
        "dev_server_port": env.int("DJANGO_VITE_PORT", default=5173),
        "manifest_path": BASE_DIR / "static" / ".vite" / "manifest.json",
    }
}
