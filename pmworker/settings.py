from celery.loaders.default import Loader


def get_settings():
    loader = Loader(app=None)
    settings = loader.read_configuration(fail_silently=False)
    return settings
