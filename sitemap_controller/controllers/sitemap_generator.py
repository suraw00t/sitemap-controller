from sitemap_controller.controllers.writer import XMLWriter
import os
import logging
from sitemap_controller import data

logger = logging.getLogger(__name__)


class SitemapGenerator:
    settings = None

    def __init__(self, settings):
        self.settings = settings
        self.article = data.Article(self.settings)
        self.free_question = data.FreeQuestion(self.settings)
        self.lawyer = data.Lawyer(self.settings)
        self.blog = data.Blog(self.settings)
        self.all_paths = []

    async def generate_sitemap(self):
        exclude_paths = self.settings.EXCLUDE_PATHS
        if os.environ.get("CONTROLLER_ENV") == "PRODUCTION":
            if not os.path.exists("/deployment/sitemap_controller"):
                os.makedirs("/deployment/sitemap_controller")
            out_file = "/deployment/sitemap_controller/sitemap.xml"
        else:
            out_file = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "../../", "sitemap.xml"
            )

        await self.get_url_paths()
        xml_writer = XMLWriter(out_file, self.settings)
        await xml_writer.write(
            [path for path in self.all_paths if path and path not in exclude_paths]
        )

    async def get_url_paths(self):
        try:
            article_paths = await self.article.get_article_paths_by_type()
            self.all_paths.extend(article_paths)

            free_question_paths = await self.free_question.get_free_question_paths()
            self.all_paths.extend(free_question_paths)

            lawyer_paths = await self.lawyer.get_lawyer_paths()
            self.all_paths.extend(lawyer_paths)

            blog_paths = await self.blog.get_blog_paths()
            self.all_paths.extend(blog_paths)
        except Exception as e:
            logger.debug("Has some error: ", repr(str(e)))
