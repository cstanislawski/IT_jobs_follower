"""
Module for handling JustJoinIT (https://justjoin.it/?tab=with-salary) offers tracker.
"""
from re import findall  # pylint: disable=W0611
from json import loads
from collections import OrderedDict
from statistics import mean
from requests import Session  # pylint: disable=E0401
from requests.adapters import HTTPAdapter, Retry  # pylint: disable=E0401
from yaml import load, SafeLoader  # pylint: disable=E0401


class JustJoinIT:  # pylint: disable=R0903
    """
    Class processing data from JustJoinIT sites.
    """

    __API_URL = "https://justjoin.it/api/offers/"
    __OFFERS_URL = "https://justjoin.it/offers/"

    def __init__(self) -> None:
        with open(file="config.yaml", mode="r", encoding="utf-8") as config_file:
            self.jji_config = load(stream=config_file, Loader=SafeLoader)["jji"]
        self.data_sources = self.jji_config["data_sources"]
        self.content = []

    def load_offers(self) -> None:
        """
        Loads all the offers present in data_sources, searches pages matching search_regex

        Analysis of URL:
        https://justjoin.it/ +
        {remote/all}/ +
        {all - idk}/ +
        {junior,mid,senior,all}/ +
        {20k min salary}/ +
        {100k max salary} +
        ?q=DevOps@category;Java@category;Docker@skill;AWS@skill&employmentType=b2b&tab=with-salary

        What's queried:
        categories, skills
        What's filtered out on the browser side:
        salary, employement type, whether remote or not

        How to complete a link:
        https://justjoin.it/offers/ + single_dict["id"]

        How to check whether an offer is available for the city:
        - dictionary within "multilocation", which looks like {"city":"some_city", (...)}
        - "city" key within the offer's dictionary

        category = marker_icon

        API URL:
        https://justjoin.it/api/offers/search?categories[]=DevOps&categories[]=Java&skills[]=Docker&skills[]=AWS


        Example URLs, https://justjoin.it/ + :
        1. all/all/mid/20k?q=DevOps@category;Java@category;Docker@skill;AWS@skill&employmentType=b2b
        2. remote?q=DevOps@category&employmentType=b2b&tab=with-salary

        """
        session = Session()
        retries = Retry(total=5, backoff_factor=1)
        session.mount("https://", HTTPAdapter(max_retries=retries))
        request = loads(session.get(self.__API_URL).content.decode("utf-8"))
        for src in self.data_sources:
            config = self.__parse_url_config(src)
            offers = self.__filter_out_offers(config, request)
            self.content.append(
                {
                    "name": src["label"],
                    "offers": [
                        OrderedDict(
                            [
                                ("id", offer[0]["id"]),
                                ("job_name", offer[0]["title"]),
                                ("url", self.__OFFERS_URL + offer[0]["id"]),
                                ("employment_types", offer[0]["employment_types"]),
                                ("avg_salary", offer[1]),
                            ]
                        )
                        for offer in offers
                    ],
                }
            )

    def __parse_url_config(self, data_source_config: dict) -> dict:
        _ = findall(pattern=r"[A-z]+@category", string=data_source_config["url"])
        categories = (
            [category.replace("@category", "").lower() for category in _] if len(_) > 0 else []
        )
        _ = findall(pattern=r"[A-z]+@skill", string=data_source_config["url"])
        skills = [skill.replace("@skill", "") for skill in _] if len(_) > 0 else []
        _ = findall(pattern=r"employmentType=[0-z]+", string=data_source_config["url"])
        employment_type = _[0].replace("employmentType=", "") if len(_) == 1 else "all"
        remote_only = "/remote" in data_source_config["url"]
        discosed_salary = "tab=with-salary" in data_source_config["url"]
        _ = findall(
            pattern=r"junior|mid|senior",
            string=data_source_config["url"]
            .replace("https://justjoin.it/", "")
            .replace(findall(pattern="q=[0-z]*", string=data_source_config["url"])[0], ""),
        )
        experience_level = _[0] if len(_) == 1 else "all"
        _ = findall(pattern=r"[0-9]+k", string=data_source_config["url"])
        min_salary = _[0] if (len(_) >= 1 and discosed_salary) else None
        return {
            "categories": categories,
            "skills": skills,
            "remote_only": remote_only,
            "employment_type": employment_type,
            "discosed_salary": discosed_salary,
            "experience_level": experience_level,
            "min_salary": min_salary,
        }

    def __filter_out_offers(self, config: dict, offers: list[dict]):  # pylint: disable=R0912
        valid_offers = []
        for single_offer in offers:
            valid = True

            if single_offer["marker_icon"] not in config["categories"]:
                valid = False

            if valid and config["skills"]:
                looked_for_skills = (
                    single_skill["name"] for single_skill in single_offer["skills"]
                )
                if not all(skill in looked_for_skills for skill in config["skills"]):
                    valid = False

            if valid and config["remote_only"] and not single_offer["remote"]:
                valid = False

            if valid and config["employment_type"] != "all":
                offer_types = (
                    employment_type["type"] for employment_type in single_offer["employment_types"]
                )
                if config["employment_type"] not in offer_types:
                    valid = False

            if valid and config["discosed_salary"]:
                salaries = (
                    employment_type["salary"]
                    for employment_type in single_offer["employment_types"]
                )
                if None in salaries:
                    valid = False

            if (
                valid
                and config["experience_level"] != "all"
                and config["experience_level"] != single_offer["experience_level"]
            ):
                valid = False

            if valid and config["min_salary"]:
                min_salaries = (
                    employment_type["salary"]["from"]
                    for employment_type in single_offer["employment_types"]
                    if employment_type["salary"] is not None
                )
                if min_salaries != () and not any(
                    min_salary > int(config["min_salary"].replace("k", "000"))
                    for min_salary in min_salaries
                ):
                    valid = False

            # if valid and not single_offer['display_offer']:
            #     valid = False

            if valid:
                avgs = {}
                for single_type in single_offer["employment_types"]:
                    if single_type["salary"] is not None:
                        avgs[single_type["type"]] = mean(
                            (int(single_type["salary"]["from"]), int(single_type["salary"]["to"]))
                        )
                # Convert how info about salary is packed into a simple format of
                # employment_types: {"b2b"-"$FROM-$TO $CURRENCY", "permanent"-"$FROM-$TO $CURRENCY"}
                # if salary's not provided - set particular offer type to "NOT_PROVIDED"
                single_offer["employment_types"] = {
                    single_type[
                        "type"
                    ]: f"{single_type['salary']['from']}-{single_type['salary']['to']} {single_type['salary']['currency'].upper()}"  # pylint: disable=C0301
                    if single_type["salary"] is not None
                    else "NOT_PROVIDED"
                    for single_type in single_offer["employment_types"]
                }

                valid_offers.append((single_offer, avgs))

        return valid_offers
