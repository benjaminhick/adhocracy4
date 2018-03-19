from django.apps import AppConfig


class ImagesConfig(AppConfig):
    name = 'adhocracy4.images'
    label = 'a4images'

    def ready(self):
        import adhocracy4.files.signals  # noqa:F401
