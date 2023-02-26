"""
Module for handling NoFluffJobs (https://nofluffjobs.com/pl) offers tracker.
"""
from time import sleep
from re import findall
from requests import get  # pylint: disable=E0401
from yaml import load, SafeLoader  # pylint: disable=E0401


class NoFluffJobs:  # pylint: disable=R0903
    """
    Class processing data from NoFluffJobs sites.
    """

    __BASE_URL = "https://nofluffjobs.com/"
    __REGEX = 'pl/job[^"]*'

    def __init__(self) -> None:
        with open(file="config.yaml", mode="r", encoding="utf-8") as config_file:
            self.nfj_config = load(stream=config_file, Loader=SafeLoader)["nfj"]
        self.data_sources = self.nfj_config["data_sources"]
        self.content = []

    def load_offers(self) -> None:
        """
        Loads all the offers present in data_sources, searches pages matching __REGEX
        """
        for src in self.data_sources:
            page = 1
            while True:
                request = get(src["url"] + str(page))
                request = request.content.decode("utf-8")
                job_offers = findall(self.__REGEX, request)
                if len(job_offers) > 0:
                    content = {src["label"]: []}
                    for job in job_offers:
                        content[src["label"]].append(
                            {
                                "id": str(findall(r"([\d\w]+(\-[\d\w]+)+)", job)[0][1]).replace(
                                    "-", ""
                                ),
                                "job_name": findall(r"([\d\w]+(\-[\d\w]+)+)", job)[0][0],
                                "url": self.__BASE_URL + job,
                            }
                        )
                    page += 1
                    self.content.append(content)
                else:
                    break
                sleep(0.1)
