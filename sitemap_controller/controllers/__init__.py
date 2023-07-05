from .server import ControllerServer
from .sitemap_generator import SitemapGenerator

__all__ = ["ControllerServer", "SitemapGenerator"]


def create_server():
    from sitemap_controller.utils.settings import get_settings

    settings = get_settings()
    server = ControllerServer(settings)

    return server
