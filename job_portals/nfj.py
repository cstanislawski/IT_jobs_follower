from requests import get
from time import sleep
from re import findall
from yaml import load, SafeLoader


class nfj:
    def __init__(self):
        with open(file="config.yaml", mode="r") as f:
            self.nfj_config = load(stream=f, Loader=SafeLoader)["nfj"]
        self.base_url = self.nfj_config["base_url"]
        self.url_search_regex = self.nfj_config["regex"]
        self.data_sources = self.nfj_config["data_sources"]

    def load_todays_offers(self):
        """
        Loads all the offers present in the URL, within all the pages matching self.url_search_regex
        """
        self.content = []
        for src in self.data_sources:
            page = 1
            while True:
                r = get(src['url'] + str(page))
                r = r.content.decode("utf-8")
                job_offers = findall(self.url_search_regex, r)
                if len(job_offers) > 0:
                    content = {src['label']: []}
                    for job in job_offers:
                        content[src['label']].append(
                            {
                                "id": str(findall(r"([\d\w]+(\-[\d\w]+)+)", job)[0][1]).replace(
                                    "-", ""
                                ),
                                "job_name": findall(r"([\d\w]+(\-[\d\w]+)+)", job)[0][0],
                                "url": self.base_url + job,
                            }
                        )
                    page += 1
                    self.content.append(content)
                else:
                    break
                sleep(0.1)

