# Django settings for usfevent project.
# Let Python generate the absolute path name 
import os
DIRNAME = os.path.dirname(__file__)
DIR_ABS = os.path.dirname(os.path.abspath(__file__))



# This retrieves the directory path of current file
# Example: /home/vincent/Code/usfevent
# DIRNAME_ABSOLUTE = os.path.dirname(os.path.abspath(__file__))


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {

    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'usfevent',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1


# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
# User uploaded files belong to media folder
# This points to a directory on your hard drive
# MEDIA_ROOT = os.path.join(DIRNAME, '/media')
MEDIA_ROOT = 'media/'





# URL that handles the media served from MEDIA_ROOT. Make sure to use a

# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
# This is the URL parent used for accessing this file
MEDIA_URL = '/webhost_media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
# STATIC_ROOT = os.path.join(DIRNAME, '/static')
STATIC_ROOT = DIR_ABS + "/static"

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.

# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    #STATIC_ROOT,
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


# Make this unique, and don't share it with anybody.
SECRET_KEY = '#90glw&ozax8f=r2)x6hlg96r(g$!78kt_irn59b5$v0hipp=9'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)


# Detect system and change slashes in directory path
if(DIR_ABS.rfind("\\") != -1): # Windows
    rooturldir = DIR_ABS[DIR_ABS.rfind("\\") + 1: ]
elif(DIR_ABS.rfind("/") != -1): # Unix
    rooturldir = DIR_ABS[DIR_ABS.rfind("/") + 1: ]

ROOT_URLCONF = rooturldir + '.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.abspath("templates")
)

TEMPLATE_CONTEXT_PROCESSORS = (  
    "django.core.context_processors.auth", 
    "django.core.context_processors.request"  
) 

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'taggit', # 3rd-party #
    'south', # 3rd-party #
    'event',
    'accounts',
)

AUTHENTICATION_BACKENDS = (
    'usfevent.backends.EmailAuthBackEnd',
    'django.contrib.auth.backends.ModelBackend',
	)

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'donsaffair@gmail.com'
EMAIL_HOST_PASSWORD = 'mypassword123'

