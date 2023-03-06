"""
Module for handling NoFluffJobs (https://nofluffjobs.com/pl) offers tracker.
"""
from time import sleep
from re import findall
from collections import OrderedDict
from statistics import mean
from requests import Session  # pylint: disable=E0401
from requests.adapters import HTTPAdapter, Retry  # pylint: disable=E0401
from yaml import load, SafeLoader  # pylint: disable=E0401


class NoFluffJobs:  # pylint: disable=R0903
    """
    Class processing data from NoFluffJobs sites
    """

    __BASE_URL = "https://nofluffjobs.com/"
    __OFFERS_REGEX = r'pl/job[^"]*'
    __OFFER_TYPE_PERMANENT_REGEX = r"permanent:{[^}]+}"
    __OFFER_TYPE_B2B_REGEX = r"b2b:{[^}]+}"
    __CURRENCY_REGEX = r"currency:([A-z]+),"
    __RANGE_REGEX = r"range:\[([^\]]+)\]"
    __PERIOD_REGEX = r"period:([A-z]+)"
    __RETRIES = 5

    def __init__(self) -> None:
        with open(file="config.yaml", mode="r", encoding="utf-8") as config_file:
            self.nfj_config = load(stream=config_file, Loader=SafeLoader)["nfj"]
        self.data_sources = self.nfj_config["data_sources"]
        self.content = []

    def load_offers(self) -> None:
        """
        Loads all the offers present in data_sources, searches pages matching __OFFERS_REGEX
        """
        for src in self.data_sources:
            page = 1
            content = {"name": src["label"], "offers": []}
            while True:
                session = Session()
                retries = Retry(total=self.__RETRIES, backoff_factor=1)
                session.mount("https://", HTTPAdapter(max_retries=retries))
                job_offers = findall(
                    self.__OFFERS_REGEX, session.get(src["url"] + str(page)).content.decode("utf-8")
                )
                if len(job_offers) > 0:
                    for offer in job_offers:
                        employment_info, average_salaries = self.__find_offer_content(offer)
                        content["offers"].append(
                            self.__prepare_final_offer(offer, employment_info, average_salaries)
                        )
                    page += 1
                    sleep(0.2)
                else:
                    if content["offers"]:
                        self.content.append(content)
                    break

    def __find_offer_content(self, offer: dict):
        session = Session()
        retries = Retry(total=self.__RETRIES, backoff_factor=1)
        session.mount("https://", HTTPAdapter(max_retries=retries))
        offer_page = session.get(self.__BASE_URL + offer).content.decode("utf-8").replace("&q;", "")

        permanent, permanent_avg = self.__find_salary(self.__OFFER_TYPE_PERMANENT_REGEX, offer_page)
        b2b, b2b_avg = self.__find_salary(self.__OFFER_TYPE_B2B_REGEX, offer_page)

        employment_types = OrderedDict()
        avgs = OrderedDict()
        if b2b:
            employment_types["b2b"] = b2b
            avgs["b2b"] = b2b_avg
        if permanent:
            employment_types["permanent"] = permanent
            avgs["permanent"] = permanent_avg

        return employment_types, avgs

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
                avg_salary = mean(int(float(x) / 12) for x in salary_range.split(","))
                salary_range = "-".join(
                    ((str(int(float(x) / 12)) for x in salary_range.split(",")))
                )
            else:
                avg_salary = mean(int(x) for x in salary_range.split(","))
                salary_range = "-".join(salary_range.split(","))
            return f"{salary_range} {currency}", avg_salary
        return None, None

    def __prepare_final_offer(self, offer, employment_info, average_salaries):
        return OrderedDict(
            [
                (
                    "id",
                    str(findall(r"([\d\w]+(\-[\d\w]+)+)", offer)[0][1]).replace("-", ""),
                ),
                ("job_name", findall(r"([\d\w]+(\-[\d\w]+)+)", offer)[0][0]),
                ("url", self.__BASE_URL + offer),
                ("employment_types", employment_info),
                ("avg_salary", average_salaries),
            ]
        )
