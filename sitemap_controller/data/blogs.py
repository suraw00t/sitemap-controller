import requests
import logging

logger = logging.getLogger(__file__)


class Blog:
    def __init__(self, settings):
        self.settings = settings
        self.strapi_api_base_url = (
            self.settings.STRAPI_API_BASE_URL
            if self.settings.STRAPI_API_BASE_URL.endswith("/")
            else self.settings.STRAPI_API_BASE_URL + "/"
        )

    async def get_blogs(self, page_size=1):
        url = self.strapi_api_base_url + "blogs"
        params = {
            "pagination[page]": 1,
            "pagination[pageSize]": page_size,
            "fields[0]": "id",
            "fields[1]": "publishedAt",
        }
        try:
            response = requests.get(url=url, params=params)
            response_json = response.json()
        except Exception as e:
            logger.debug("...", url, "has error", repr(str(e)))
        finally:
            response.close()

        return response_json

    async def get_blog_paths(self):
        paths = []
        blogs = await self.get_blogs()
        page_count = blogs["meta"]["pagination"]["pageCount"]
        blogs = await self.get_blogs(page_count)
        root_path = "blogs"
        for data in blogs["data"]:
            if data["attributes"]["publishedAt"] != None:
                paths.append("{}/{}".format(root_path, data["id"]))

        return paths
