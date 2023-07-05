from aiofile import AIOFile, Writer
import logging

logger = logging.getLogger(__file__)


class XMLWriter:
    def __init__(self, filename: str, settings=None):
        self.filename = filename
        self.settings = settings

    async def write(self, url_paths):
        async with AIOFile(self.filename, "w") as aiodf:
            writer = Writer(aiodf)
            base_url = (
                self.settings.BASE_URL
                if self.settings.BASE_URL.endswith("/")
                else self.settings.BASE_URL + "/"
            )
            await writer('<?xml version="1.0" encoding="utf-8"?>\n')
            await writer(
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
                ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
                ' xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">\n'
            )
            await aiodf.fsync()
            for url_path in url_paths:
                await writer("<url><loc>{}{}</loc></url>\n".format(base_url, url_path))
            await aiodf.fsync()

            await writer("</urlset>")
            await aiodf.fsync()

        logger.info(f"Writen at {self.filename}")
