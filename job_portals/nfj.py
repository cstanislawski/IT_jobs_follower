"""
Module for handling NoFluffJobs (https://nofluffjobs.com/pl) offers tracker.
"""
from time import sleep
from re import findall
from collections import OrderedDict
from requests import Session  # pylint: disable=E0401
from requests.adapters import HTTPAdapter, Retry  # pylint: disable=E0401
from yaml import load, SafeLoader  # pylint: disable=E0401


class NoFluffJobs:  # pylint: disable=R0903
    """
    Class processing data from NoFluffJobs sites.
    """

    __BASE_URL = "https://nofluffjobs.com/"
    __OFFERS_REGEX = r'pl/job[^"]*'
    __OFFER_TYPE_PERMANENT_REGEX = r"permanent:{[^}]+}"
    __OFFER_TYPE_B2B_REGEX = r"b2b:{[^}]+}"
    __CURRENCY_REGEX = r"currency:([A-z]+),"
    __RANGE_REGEX = r"range:\[([^\]]+)\]"
    __PERIOD_REGEX = r"period:([A-z]+)"

    def __init__(self) -> None:
        with open(file="config.yaml", mode="r", encoding="utf-8") as config_file:
            self.nfj_config = load(stream=config_file, Loader=SafeLoader)["nfj"]
        self.data_sources = self.nfj_config["data_sources"]
        self.content = []

    def load_offers(self) -> None:
        """
        Loads all the offers present in data_sources, searches pages matching __OFFERS_REGEX
        """
        retries = 5
        for src in self.data_sources:
            page = 1
            content = {src["label"]: []}
            while True:
                session = Session()
                retries = Retry(total=5, backoff_factor=1)
                session.mount("https://", HTTPAdapter(max_retries=retries))
                job_offers = findall(
                    self.__OFFERS_REGEX, session.get(src["url"] + str(page)).content.decode("utf-8")
                )
                if len(job_offers) > 0:
                    for offer in job_offers:
                        content[src["label"]].append(
                            OrderedDict(
                                [
                                    (
                                        "id",
                                        str(findall(r"([\d\w]+(\-[\d\w]+)+)", offer)[0][1]).replace(
                                            "-", ""
                                        ),
                                    ),
                                    ("job_name", findall(r"([\d\w]+(\-[\d\w]+)+)", offer)[0][0]),
                                    ("url", self.__BASE_URL + offer),
                                    ("employment_types", self.__find_employment_info(offer)),
                                ]
                            )
                        )
                    page += 1
                    sleep(0.2)
                else:
                    if content != {src["label"]: []}:
                        self.content.append(content)
                    break

    def __find_employment_info(self, offer: dict):
        session = Session()
        retries = Retry(total=5, backoff_factor=1)
        session.mount("https://", HTTPAdapter(max_retries=retries))
        offer_page = session.get(self.__BASE_URL + offer).content.decode("utf-8").replace("&q;", "")

        permanent = self.__find_salary(self.__OFFER_TYPE_PERMANENT_REGEX, offer_page)
        b2b = self.__find_salary(self.__OFFER_TYPE_B2B_REGEX, offer_page)

        employment_types = OrderedDict()
        if b2b:
            employment_types["b2b"] = b2b
        if permanent:
            employment_types["permanent"] = permanent

        return employment_types

    def __find_salary(self, regex: str, page_content: str):
        all_salary_info = findall(regex, page_content)
        if len(all_salary_info) >= 2:
            all_salary_info = all_salary_info[2]
            currency = findall(self.__CURRENCY_REGEX, page_content)[0]
            salary_range = findall(self.__RANGE_REGEX, all_salary_info)[0]
            period = findall(self.__PERIOD_REGEX, all_salary_info)[0]
            if period != "Month":
                # If provided salary is not a month, then it's annual
                # If so, divide the provided amount by num of months
                salary_range = "-".join(
                    ((str(int(float(x) / 12)) for x in salary_range.split(",")))
                )
            else:
                salary_range = "-".join(salary_range.split(","))
            return f"{salary_range} {currency}"
        return "NOT_FOUND"
