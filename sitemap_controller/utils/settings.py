from . import Config


def get_settings():
    settings = Config()
    settings.from_object("sitemap_controller.default_settings")
    settings.from_envvar("SITEMAP_CONTROLLER_SETTINGS", silent=True)

    return settings
