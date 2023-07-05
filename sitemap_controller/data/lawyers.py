import requests
import logging

logger = logging.getLogger(__file__)


class Lawyer:
    def __init__(self, settings):
        self.settings = settings
        self.api_base_url = (
            self.settings.API_BASE_URL
            if self.settings.API_BASE_URL.endswith("/")
            else self.settings.API_BASE_URL + "/"
        )

    async def get_lawyers(self, limit=1):
        url = self.api_base_url + "lawyer/find-lawyers"
        body = {"limit": limit, "page": 1}

        try:
            response = requests.post(url, json=body)
            response_json = response.json()
        except Exception as e:
            logger.debug("...", url, "has error", repr(str(e)))
        finally:
            response.close()

        return response_json

    async def get_lawyer_paths(self):
        paths = []
        lawyers = await self.get_lawyers()
        total_lawyers = lawyers["data"]["total"]
        lawyers = await self.get_lawyers(total_lawyers)
        root_path = "lawyers"
        for data in lawyers["data"]["items"]:
            if data["isSetupedService"] == True:
                paths.append("{}/{}".format(root_path, data["id"]))

        return paths
