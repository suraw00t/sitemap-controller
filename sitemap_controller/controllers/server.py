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

    def time_schedule(self, schedule=None):
        hours, minutes, dom, months, dow = schedule.split(" ")
        today = datetime.datetime.today()
        hours = int(hours) if hours != "*" else 0
        minutes = int(minutes) if minutes != "*" else 0
        day = int(dom) if dom != "*" else today.day
        month = int(months) if months != "*" else today.month
        dow = int(dow) if dow != "*" else None
        year = today.year

        if months == "*" and dom != "*" and day <= today.day:
            month = month + 1

        if hours <= today.hour and minutes <= today.minute and dom == "*":
            day = day + 1

        if (
            month <= today.month
            and day <= today.day
            and hours <= today.hour
            and minutes < today.minute
        ):
            year = year + 1
        elif month < today.month and day <= today.day:
            year = year + 1

        if dow is not None:
            print("days of week", dow)

        date_time = datetime.datetime(year, month, day, hours, minutes, 0, 0)
        schedule = abs(datetime.datetime.today() - date_time)
        logger.info(f"next task at {date_time} : remaining {schedule}")
        return schedule

    async def controller_schedule(self):
        logger.debug("start controller schedule")
        time_check_schedule = self.settings.get("SCHEDULE_TO_CHECK_SITEMAP")
        # await self.sitemap.generate_sitemap()

        while self.running:
            logger.debug("running sitemap controller")
            schedule = self.time_schedule(time_check_schedule)
            await asyncio.sleep(schedule.total_seconds())
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
