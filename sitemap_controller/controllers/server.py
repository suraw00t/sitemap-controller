import signal
import asyncio
import logging
import datetime
from .sitemap_controller import SitemapController
from sitemap_controller.crawler import Crawler

logger = logging.getLogger(__name__)


class ControllerServer:
    def __init__(self, settings):
        self.settings = settings
        self.running = False

        self.sitemap = SitemapController(self.settings)

    async def controller_schedule(self):
        logger.debug("start controller schedule")
        time_check = self.settings.get("SCHEDULE_TO_CHECK_SITEMAP")
        hours, minutes, dom, month, dow = time_check.split(" ")
        process_time = datetime.time(int(hours), int(minutes), 0)
        # ทำเวลาให้ใช้งานได้
        await self.sitemap.generate_sitemap()

        while self.running:
            logger.debug("running schedule sitemap controller")

            date = datetime.date.today()
            time_set = datetime.datetime.combine(date, process_time)
            time_to_check = time_set - datetime.datetime.now()
            await asyncio.sleep(time_to_check.seconds)
            await self.sitemap.generate_sitemap()

            await asyncio.sleep(10)

    async def set_up(self):
        logging.basicConfig(
            format="%(asctime)s - %(name)s:%(levelname)s:%(lineno)d - %(message)s",
            datefmt="%d-%b-%y %H:%M:%S",
            level=logging.DEBUG,
        )

    def run(self):
        self.running = True
        loop = asyncio.get_event_loop()
        loop.set_debug(True)
        loop.run_until_complete(self.set_up())
        loop.create_task(self.controller_schedule())

        try:
            loop.run_forever()
        except Exception as e:
            self.running = False
        finally:
            loop.close()
