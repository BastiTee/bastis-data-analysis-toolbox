"""Django-Wrapper."""

from django.conf.urls import url
from os import path, environ
from django.http import HttpResponse
from django.template import Template, Context

BASE_DIR = path.dirname(path.dirname(__file__))
SECRET_KEY = 'secret_key'
DEBUG = True
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'django_wrapper',
)
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
    """Handles rendering of HTTP responses."""

    def get(self, request):
        """Serve GET responses."""
        template_dir = path.join('django_wrapper', 'static')
        templates = [
            _read_file_to_string(path.join(template_dir, 'header.html')),
            _read_file_to_string(path.join(template_dir,
                                           environ['ROBOTA_TEMPLATE'])),
            _read_file_to_string(path.join(template_dir, 'footer.html')),
        ]
        t = Template('\n'.join(templates))
        c = Context({'infile': environ['ROBOTA_INPUT']})
        return HttpResponse(t.render(c))


urlpatterns = [
    url(r'^', ViewHandler().get, name='get')
]