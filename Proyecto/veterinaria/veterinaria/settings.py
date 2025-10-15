from pathlib import Path        # Importa Path para manejo de rutas del sistema

# CONFIGURACION DE RUTAS BASE
BASE_DIR = Path(__file__).resolve().parent.parent  # Obtiene la ruta base del proyecto 

# CONFIGURACION DE SEGURIDAD
SECRET_KEY = 'django-insecure-uk(=no1^l1al$a8cs=j*ar_6pt^_v4lwgg4bn8+r%pgf(wit2!'  
DEBUG = True                                                
ALLOWED_HOSTS = []  

# APLICACIONES INSTALADAS
INSTALLED_APPS = [
    'django.contrib.admin',        # App de administracion de Django
    'django.contrib.auth',         # Sistema de autenticacion
    'django.contrib.contenttypes', # Sistema de tipos de contenido
    'django.contrib.sessions',     # Manejo de sesiones
    'django.contrib.messages',     # Sistema de mensajes
    'django.contrib.staticfiles',  # Manejo de archivos estaticos
    'usuarios',                    # App personalizada para usuarios
    'servicios',                   # App personalizada para servicios
    'citas',                       # App personalizada para citas
    'administrador',               # App del administrador
]

# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',            # Middleware de seguridad
    'django.contrib.sessions.middleware.SessionMiddleware',     # Manejo de sesiones
    'django.middleware.common.CommonMiddleware',                # Funcionalidades comunes
    'django.middleware.csrf.CsrfViewMiddleware',                # Proteccion CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Autenticacion de usuarios
    'django.contrib.messages.middleware.MessageMiddleware',     # Manejo de mensajes
    'django.middleware.clickjacking.XFrameOptionsMiddleware',   # Proteccion clickjacking
]

# CONFIGURACION DE URLs
ROOT_URLCONF = 'veterinaria.urls'  # Archivo principal de URLs del proyecto

# CONFIGURACION DE PLANTILLAS
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',   # Motor de plantillas Django
        'DIRS': [BASE_DIR / 'templates'],                               # Directorios adicionales para plantillas
        'APP_DIRS': True,                                               # Buscar plantillas en directorios de apps
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',           # Procesador de request
                'django.contrib.auth.context_processors.auth',          # Procesador de autenticacion
                'django.contrib.messages.context_processors.messages',  # Procesador de mensajes
                'django.template.context_processors.media',             # Procesador para archivos media
            ],
        },
    },
]

# CONFIGURACION WSGI
WSGI_APPLICATION = 'veterinaria.wsgi.application'  # Aplicacion WSGI para despliegue

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
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',  # Valida similitud con atributos del usuario
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',            # Valida longitud minima
        'OPTIONS': {
            'min_length': 16,  # 16 caracteres minimo
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',           # Valida contrasenas comunes
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',          # Valida contrasenas numericas
    },
]

# CONFIGURACION DEL MODELO DE USUARIO
AUTH_USER_MODEL = 'usuarios.Usuario'    # Modelo de usuario personalizado

# CONFIGURACION INTERNACIONAL
LANGUAGE_CODE = 'es-es'                 
TIME_ZONE = 'America/Mexico_City'       
USE_I18N = True                         
USE_TZ = True                           

# CONFIGURACION DE ARCHIVOS ESTATICOS Y MEDIOS
STATIC_URL = 'static/'                      
STATICFILES_DIRS = [BASE_DIR / 'static']    
STATIC_ROOT = BASE_DIR / 'staticfiles'      

# CONFIGURACION DE ARCHIVOS MEDIOS (para imagenes de servicios)
MEDIA_URL = '/media/'  
MEDIA_ROOT = BASE_DIR / 'media'  

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'  

# CONFIGURACION AUTENTICACION
LOGIN_URL = 'login'         # URL para redireccionar al login
LOGIN_REDIRECT_URL = '/'    # URL de redireccion despues del login para usuarios normales
LOGOUT_REDIRECT_URL = '/'   # URL de redireccion despues del logout

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

# CONFIGURACION DE CORREO (Para confirmaciones de citas)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'    
EMAIL_HOST = 'smtp.gmail.com'                                       
EMAIL_PORT = 587  
EMAIL_USE_TLS = True  
EMAIL_HOST_USER = 'tu_email@gmail.com'  
EMAIL_HOST_PASSWORD = 'tu_password'  
DEFAULT_FROM_EMAIL = 'veterinaria@example.com'  

# CONFIGURACION DE SEGURIDAD ADICIONAL
if DEBUG:
    import mimetypes
    mimetypes.add_type("application/javascript", ".js", True)  
    
    # Mostrar emails en consola
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    
    # Para debug de archivos media en desarrollo
    from django.urls import include, path
    urlpatterns = [
        #URLs
    ]
    
    # Servir archivos media 
    from django.conf.urls.static import static
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)

# CONFIGURACION PARA EL PANEL DE ADMINISTRADOR
ADMIN_SITE_HEADER = "Sistema de Veterinaria - Panel de Administracion"  # Encabezado del panel admin
ADMIN_SITE_TITLE = "Veterinaria Admin"                                  # Titulo del panel admin
ADMIN_INDEX_TITLE = "Bienvenido al Panel de Administracion"             # Titulo del indice admin

# MENSAJES PERSONALIZADOS
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',   
    messages.INFO: 'info',         
    messages.SUCCESS: 'success',   
    messages.WARNING: 'warning',   
    messages.ERROR: 'danger',      
}