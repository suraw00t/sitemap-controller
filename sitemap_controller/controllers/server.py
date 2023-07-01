import signal
import asyncio
import logging
import datetime
from .sitemap_controller import SitemapController
from sitemap_controller.crawler import Crawler

logger = logging.getLogger(__name__)


def find_next_date_from_weekday(weekday=None):
    if weekday is None or weekday not in range(0, 7):
        return
    today = datetime.datetime.today()
    if today.weekday() == weekday:
        return today
    elif today.weekday() < weekday:
        time_delta = datetime.timedelta(days=weekday - today.weekday())
        return today + time_delta
    else:
        time_delta = datetime.timedelta(days=7 - weekday - today.weekday())
        return today + time_delta


def datetime_schedule(schedule=None):
    hours, minutes, dom, months, dow = schedule.strip().split(" ")
    today = datetime.datetime.today()
    hours = int(hours) if hours != "*" else 0
    minutes = int(minutes) if minutes != "*" else 0
    day = int(dom) if dom != "*" else today.day
    month = int(months) if months != "*" else today.month
    dow = int(dow) if dow != "*" else None
    year = today.year

    time_today = today.time()
    time = datetime.time(hours, minutes, 0, 0)
    date = datetime.date(today.year, month if month != today.month else month, day)
    current_datetime = datetime.datetime.combine(date, time)

    if months != "*" and dom == "*":
        day = 1

    if time < time_today and months == "*" and dom == "*":
        day = day + 1

    if current_datetime < today and dom != "*" and months == "*":
        month = month + 1

    if current_datetime < today and months != "*":
        year = year + 1

    if dow is not None:
        day_of_week = find_next_date_from_weekday(dow)
        if day_of_week.day == today.day and time < time_today:
            day = day_of_week.day + 7
        else:
            day = day_of_week.day

    date_time = datetime.datetime(year, month, day, hours, minutes, 0, 0)
    schedule = abs(datetime.datetime.today() - date_time)
    logger.info(f"next task at {date_time} : remaining {schedule}")
    return schedule


class ControllerServer:
    def __init__(self, settings):
        self.settings = settings
        self.running = False

        self.sitemap = SitemapController(self.settings)

    async def controller_schedule(self):
        logger.debug("start controller schedule")
        time_check_schedule = self.settings.get("SCHEDULE_TO_CHECK_SITEMAP")
        await self.sitemap.generate_sitemap()

        while self.running:
            logger.debug("running sitemap controller")
            schedule = datetime_schedule(time_check_schedule)
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
