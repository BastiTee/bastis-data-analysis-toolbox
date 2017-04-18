"""Django-Wrapper."""

from django.conf.urls import url
from os import path, environ

print(environ['ROBOTA_HOST'])

BASE_DIR = path.dirname(path.dirname(__file__))
SECRET_KEY = 'secret_key'
DEBUG = True
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'django_wrapper',
)
# print('--- static dir = ' + environ['ROBOTA_STATIC'])
# STATIC_ROOT = environ['ROBOTA_STATIC']
STATIC_URL = '/static/'
ROOT_URLCONF = 'django_wrapper.django'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': []
        },
    },
]


def _read_file_to_string(filename):
    content = []
    ofile = open(filename)
    for line in ofile:
        line = line.strip()
        if not line:
            continue
        content.append(line)
    ofile.close()
    return '\n'.join(content)


class ViewHandler ():
    """tbd."""

    def get(self, request):
        """tbd."""
        from django.http import HttpResponse
        from django.template import Template, Context

        template_file = path.join(environ['ROBOTA_STATIC'], 'static', 'd3.html')
        print(template_file)
        template = _read_file_to_string(template_file)
        t = Template(template)
        c = Context({})
        return HttpResponse(t.render(c))


urlpatterns = [
    url(r'^', ViewHandler().get, name='get')
]
