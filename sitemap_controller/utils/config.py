import os
from configparser import RawConfigParser

from sitemap_controller import utils

settings = None


def get_settings():
    global settings

    if not settings:
        settings = RawConfigParser()
        filename = os.environ.get("SITEMAP_CONTROLLER_SETTINGS", None)
        if filename is None:
            print("This programe require SITEMAP_CONTROLLER_SETTINGS environment")
            return

        utils.from_object(settings, "sitemap_controller.default_settings")
        utils.from_envvar(
            settings,
            "SITEMAP_CONTROLLER_SETTINGS",
            silent=True,
        )

        # try:
        #     url = sitemap["URL"]
        # except:
        #     print("Not valid URL in SITEMAP_CONTROLLER_SETTINGS")
        #     url = ""

        # if len(schedule) < 5:
        #     print(
        #         """
        #         Incurrect schedule format
        #         Schedule must be format "minutes hours dom month dow"
        #         example: "0 0 * * *" means run everyday at 00:00 A.M."""
        #     )
        def get(self, option: str, default: str = ""):
            if settings.has_option(option):
                return self[option]
            else:
                return default

    return settings[settings.default_section]
