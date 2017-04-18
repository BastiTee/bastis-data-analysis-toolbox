"""Init controller for django wrapper."""
from django.apps import AppConfig
from os import environ


class DjangoWrapperConfig(AppConfig):
    """"Configuration wrapper."""

    name = 'django_wrapper'
    verbose_name = 'Robota Django Wrapper'

    def ready(self):
        """Called on template-ready event."""
        import webbrowser
        webbrowser.open(
            'http://{}:{}'.format(
                environ['ROBOTA_HOST'], environ['ROBOTA_PORT']))


default_app_config = 'django_wrapper.DjangoWrapperConfig'
