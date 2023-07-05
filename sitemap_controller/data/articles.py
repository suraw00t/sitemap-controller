import requests
import logging

logger = logging.getLogger(__file__)


class Article:
    def __init__(self, settings):
        self.settings = settings
        self.strapi_api_base_url = (
            self.settings.STRAPI_API_BASE_URL
            if self.settings.STRAPI_API_BASE_URL.endswith("/")
            else self.settings.STRAPI_API_BASE_URL + "/"
        )

    async def get_articles(self, page_size=1):
        url = self.strapi_api_base_url + "articles"
        params = {
            "pagination[page]": 1,
            "pagination[pageSize]": page_size,
            "fields[0]": "slug",
            "fields[1]": "publishedAt",
            "populate[type][fields][0]": "slug",
            "populate[articles][fields][1]": "publishedAt",
        }
        response = requests.get(url=url, params=params)
        response_json = response.json()

        return response_json

    async def get_article_types(self, page_size=1):
        url = self.strapi_api_base_url + "article-types"
        params = {
            "pagination[page]": 1,
            "pagination[pageSize]": page_size,
            "fields[0]": "slug",
            "fields[1]": "publishedAt",
            "populate[articles][fields][0]": "slug",
            "populate[articles][fields][1]": "publishedAt",
        }

        try:
            response = requests.get(url=url, params=params)
            response_json = response.json()
        except Exception as e:
            logger.debug("...", url, "has error", repr(str(e)))
        finally:
            response.close()

        return response_json

    async def get_article_paths_by_type(self):
        paths = []
        article_types = await self.get_article_types()
        page_count = article_types["meta"]["pagination"]["pageCount"]
        article_types = await self.get_article_types(page_count)

        for type_data in article_types["data"]:
            article_type_data = type_data["attributes"]
            root_path = article_type_data["slug"]

            if article_type_data["publishedAt"] != None:
                for data in article_type_data["articles"]["data"]:
                    if data["attributes"]["publishedAt"] != None:
                        paths.append(
                            "{}/{}/{}".format(
                                "articles", root_path, data["attributes"]["slug"]
                            )
                        )

        return paths
