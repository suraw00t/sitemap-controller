import os
import logging
from sitemap_controller.crawler import Crawler

logger = logging.getLogger(__name__)


class SitemapController:
    settings = None

    def __init__(self, settings):
        self.settings = settings

    async def generate_sitemap(self):
        exclude_urls = self.settings.EXCLUDE_URLS
        root_url = self.settings.URL
        if os.environ.get("CONTROLLER_ENV") == "PRODUCTION":
            if not os.path.exists("/deployment/sitemap_controller"):
                os.makedirs("/deployment/sitemap_controller")
            out_file = "/deployment/sitemap_controller/sitemap.xml"
        else:
            out_file = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "../../", "sitemap.xml"
            )

        http_request_options = {"ssl": self.settings.HTTP_REQUEST_SSL_OPTION}
        logger.debug(self.settings)

        crawler = Crawler(
            rooturl=root_url,
            out_file=out_file,
            http_request_options=http_request_options,
        )
        crawler.set_exclude_url(urls_list=exclude_urls)
        await crawler.run()
