import asyncio
import logging
import json
import datetime
from . import sitemap_controller

logger = logging.getLogger(__name__)


class ControllerServer:
    def __init__(self, settings):
        self.settings = settings
        self.running = False

        self.sitemap = sitemap_controller.SitemapController(self.settings)

    async def check_evaluations_daily(self):
        time_check = self.settings["SCHEDULE_TO_CHECK_SITEMAP"]
        hour, minute = time_check.split(":")
        process_time = datetime.time(int(hour), int(minute), 0)

        while self.running:
            logger.debug("start check evaluation data daily")

            date = datetime.date.today()
            time_set = datetime.datetime.combine(date, process_time)
            time_to_check = time_set - datetime.datetime.now()
            await asyncio.sleep(time_to_check.seconds)

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

        try:
            loop.run_forever()
        except Exception as e:
            self.running = False
        finally:
            loop.close()
