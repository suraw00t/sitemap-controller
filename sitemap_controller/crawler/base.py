import logging
import asyncio
import aiohttp
import urllib
from typing import Any, Optional, MutableMapping

from .writers import TextWriter, XMLWriter
from .parsers import ReParser

logger = logging.getLogger(__file__)


class Crawler:
    format_processors = {"xml": XMLWriter, "txt": TextWriter}

    exclude_urls = []

    def __init__(
        self,
        rooturl: str,
        out_file: str,
        out_format: str = "xml",
        maxtasks: int = 100,
        todo_queue_backend: Any = set,
        done_backend: Any = dict,
        http_request_options: Optional[MutableMapping] = None,
    ):
        """
        Crawler constructor
        :param rooturl: root url of site
        :type rooturl: str
        :param out_file: file to save sitemap result
        :type out_file: str
        :param out_format: sitemap type [xml | txt]. Default xml
        :type out_format: str
        :param maxtasks: maximum count of tasks. Default 100
        :type maxtasks: int
        """
        self.rooturl = rooturl
        self.todo_queue = todo_queue_backend()
        self.busy = set()
        self.done = done_backend()
        self.tasks = set()
        self.sem = asyncio.Semaphore(maxtasks)
        self.http_request_options = http_request_options or {}

        # connector stores cookies between requests and uses connection pool
        self.session = aiohttp.ClientSession()
        self.writer = self.format_processors.get(out_format)(out_file)

        self.parser = ReParser

    def set_parser(self, parser_class):
        self.parser = parser_class

    async def run(self):
        """
        Main function to start parsing site
        :return:
        """
        t = asyncio.ensure_future(self.addurls([(self.rooturl, "")]))
        await asyncio.sleep(1)
        while self.busy:
            await asyncio.sleep(1)

        await t
        await self.session.close()
        await self.writer.write([key for key, value in self.done.items() if value])

    async def addurls(self, urls):
        """
        Add urls in queue and run process to parse
        :param urls:
        :return:
        """
        for url, parenturl in urls:
            url = urllib.parse.urljoin(parenturl, url)
            url, frag = urllib.parse.urldefrag(url)
            if (
                url.startswith(self.rooturl)
                and not any(exclude_part in url for exclude_part in self.exclude_urls)
                and url not in self.busy
                and url not in self.done
                and url not in self.todo_queue
            ):
                self.todo_queue.add(url)
                # Acquire semaphore
                await self.sem.acquire()
                # Create async task
                task = asyncio.ensure_future(self.process(url))
                # Add collback into task to release semaphore
                task.add_done_callback(lambda t: self.sem.release())
                # Callback to remove task from tasks
                task.add_done_callback(self.tasks.remove)
                # Add task into tasks
                self.tasks.add(task)

    async def process(self, url):
        """
        Process single url
        :param url:
        :return:
        """
        logger.info(f"processing: {url}")

        # remove url from basic queue and add it into busy list
        self.todo_queue.remove(url)
        self.busy.add(url)
        meta_tags = []

        try:
            resp = await self.session.get(
                url, **self.http_request_options
            )  # await response
        except Exception as exc:
            # on any exception mark url as BAD
            print("...", url, "has error", repr(str(exc)))
            self.done[url] = False
        else:
            # only url with status == 200 and content type == 'text/html' parsed
            if resp.status == 200 and ("text/html" in resp.headers.get("content-type")):
                data = (await resp.read()).decode("utf-8", "replace")
                urls = self.parser.parse(data)
                asyncio.Task(self.addurls([(u, url) for u in urls]))
                meta_tags = self.meta_parse(data)

            # even if we have no exception, we can mark url as good
            resp.close()
            # self.done[url] = True

            if not any("robots" in meta_tag for meta_tag in meta_tags):
                self.done[url] = True
            else:
                self.done[url] = False

        self.busy.remove(url)
        # logger.info(
        #     f"{len(self.done)} completed tasks, {len(self.tasks)} still pending, todo_queue {len(self.todo_queue)}"
        # )
        await asyncio.sleep(0.1)

    def set_exclude_url(self, urls_list):
        self.exclude_urls = urls_list

    def meta_parse(self, html_str) -> list:
        import re

        return re.findall(r"(<meta[^>]*>)", html_str)
