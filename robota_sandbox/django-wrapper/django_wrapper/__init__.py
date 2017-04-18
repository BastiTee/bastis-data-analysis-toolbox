from django.apps import AppConfig
from os import environ


class DjangoWrapperConfig(AppConfig):
    name = 'django_wrapper'
    verbose_name = 'Robota Django Wrapper'

    def ready(self):
        import webbrowser
        webbrowser.open(
            'http://{}:{}'.format(
                environ['ROBOTA_HOST'], environ['ROBOTA_PORT']))


default_app_config = 'django_wrapper.DjangoWrapperConfig'
