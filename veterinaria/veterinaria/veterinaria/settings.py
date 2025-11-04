from pathlib import Path
from django.contrib.messages import constants as messages
import os

# CONFIGURACION DE RUTAS BASE
BASE_DIR = Path(__file__).resolve().parent.parent

# CONFIGURACION DE SEGURIDAD
SECRET_KEY = 'django-insecure-uk(=no1^l1al$a8cs=j*ar_6pt^_v4lwgg4bn8+r%pgf(wit2!'  
DEBUG = True                                                
ALLOWED_HOSTS = []  

# APLICACIONES INSTALADAS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'usuarios',
    'servicios',
    'citas',
    'administrador',
    'acceso',
    'mascotas',
    'veterinario',
]

# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CONFIGURACION DE URLs
ROOT_URLCONF = 'veterinaria.urls'

# CONFIGURACION WSGI
WSGI_APPLICATION = 'veterinaria.wsgi.application'

# CONFIGURACION DE PLANTILLAS
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'usuarios.context_processors.veterinarios_disponibles',
            ],
        },
    },
]

# CONFIGURACION DE BASE DE DATOS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'veterinaria_db',
        'USER': 'postgres',
        'PASSWORD': 'koala',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# VALIDACIONES DE CONTRASENA
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 16,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# CONFIGURACION DEL MODELO DE USUARIO
AUTH_USER_MODEL = 'usuarios.Usuario'

# CONFIGURACION INTERNACIONAL
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Guatemala'
USE_I18N = True
USE_TZ = True

# CONFIGURACION DE ARCHIVOS ESTATICOS Y MEDIOS
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# CONFIGURACION DE ARCHIVOS MEDIOS (CORREGIDO)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CREAR DIRECTORIO MASCOTAS SI NO EXISTE (NUEVO)
try:
    MASCOTAS_MEDIA_DIR = os.path.join(MEDIA_ROOT, 'mascotas', 'fotos')
    os.makedirs(MASCOTAS_MEDIA_DIR, exist_ok=True)   
except Exception as e:
    print(f"⚠ Error creando directorio mascotas: {e}")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CONFIGURACION AUTENTICACION
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# URL ESPECIFICA PARA REDIRECCION DE ADMINISTRADORES
def get_login_redirect_url(request):
    """Redirige a administradores a su panel y a usuarios normales al home"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return '/administrador/panel/'
    return '/'

# CONFIGURACION PARA RECUERDAME - SESION PERSISTENTE
SESSION_COOKIE_AGE = 1209600
SESSION_SAVE_EVERY_REQUEST = True

# CONFIGURACION DE CORREO 
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'myvetpet6@gmail.com'
EMAIL_HOST_PASSWORD = 'hefq fabw hwgr ivlv'
DEFAULT_FROM_EMAIL = 'myvetpet6@gmail.com'
SERVER_EMAIL = 'myvetpet6@gmail.com'

# Configuración adicional para mejor manejo de correos
EMAIL_TIMEOUT = 30  # Timeout en segundos

# URLs para recuperación de contraseña
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# CONTRASEÑA INCORRECTA Y BLOQUEO
LOGIN_ATTEMPTS_LIMIT = 3
LOGIN_LOCKOUT_SECONDS = 3600
LOGIN_IP_ATTEMPTS_LIMIT = 30
LOGIN_IP_WINDOW_SECONDS = 600
LOGIN_IP_BLOCK_SECONDS = 3600

# CACHE
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "login-throttle-cache",
    }
}

# CONFIGURACION PARA EL PANEL DE ADMINISTRADOR
ADMIN_SITE_HEADER = "Sistema de Veterinaria - Panel de Administracion"
ADMIN_SITE_TITLE = "Veterinaria Admin"
ADMIN_INDEX_TITLE = "Bienvenido al Panel de Administracion"

# MENSAJES PERSONALIZADOS
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# CONFIGURACION DE SEGURIDAD ADICIONAL PARA DESARROLLO
if DEBUG:
    import mimetypes
    mimetypes.add_type("application/javascript", ".js", True)
    
    