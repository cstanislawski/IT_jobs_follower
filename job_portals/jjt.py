"""
Module for handling JustJoinIT (https://justjoin.it/?tab=with-salary) offers tracker.
"""
from re import findall  # pylint: disable=W0611
from requests import get  # pylint: disable=E0401
from yaml import load, SafeLoader  # pylint: disable=E0401


class JustJoinIT:  # pylint: disable=R0903
    """
    Class processing data from JustJoinIT sites.
    """

    def __init__(self) -> None:
        with open(file="config.yaml", mode="r", encoding="utf-8") as config_file:
            self.nfj_config = load(stream=config_file, Loader=SafeLoader)["jjt"]
        self.base_url = self.nfj_config["base_url"]
        self.data_sources = self.nfj_config["data_sources"]
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

        if we simply turn on remote, then we get

        API URL:
        https://justjoin.it/api/offers/search?categories[]=DevOps&categories[]=Java&skills[]=Docker&skills[]=AWS


        Example URLs, https://justjoin.it/ + :
        1. all/all/mid/20k?q=DevOps@category;Java@category;Docker@skill;AWS@skill&employmentType=b2b
        2. remote?q=DevOps@category&employmentType=b2b&tab=with-salary

        """
        request = get("https://justjoin.it/api/offers/")
        request = request.content.decode("utf-8")
        self.content.append(request)
