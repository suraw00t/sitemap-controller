import requests
import logging

logger = logging.getLogger(__file__)


class FreeQuestion:
    def __init__(self, settings):
        self.settings = settings
        self.strapi_api_base_url = (
            self.settings.STRAPI_API_BASE_URL
            if self.settings.STRAPI_API_BASE_URL.endswith("/")
            else self.settings.STRAPI_API_BASE_URL + "/"
        )

    async def get_free_questions(self, page_size=1):
        url = self.strapi_api_base_url + "free-questions"
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

    async def get_free_question_paths(self):
        paths = []
        free_questions = await self.get_free_questions()
        page_count = free_questions["meta"]["pagination"]["pageCount"]
        free_questions = await self.get_free_questions(page_count)
        root_path = "free-qna"
        for data in free_questions["data"]:
            if data["attributes"]["publishedAt"] != None:
                paths.append("{}/{}".format(root_path, data["id"]))

        return paths
