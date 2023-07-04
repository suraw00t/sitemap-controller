from .config import Config


class Setting:
    def __init__(self):
        self.settings = Config()

    def get_settings(self):
        self.settings.from_object("sitemap_controller.default_settings")
        self.settings.from_envvar("SITEMAP_CONTROLLER_SETTINGS", silent=True)

        return self.settings
