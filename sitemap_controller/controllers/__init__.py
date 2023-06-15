from .server import ControllerServer


def create_server():
    from sitemap_controller.utils import get_settings

    settings = get_settings()
    server = ControllerServer(settings)

    return server
