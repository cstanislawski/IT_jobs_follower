"""
Module for tracking offers on sites specified in config.yaml.
"""

from datetime import datetime
from os import path
from typing import List, Dict, Any
from collections import OrderedDict
from sys import version_info
from yaml import load, safe_dump, add_representer, SafeLoader, SafeDumper  # pylint: disable=E0401
from job_portals.nfj import NoFluffJobs
from job_portals.jji import JustJoinIT


# from job_portals.bdj import BullDogJob
# from job_portals.sj import SolidJobs


OFFERS_DIRECTORY = "offers/"
FINAL_FILE = "".join([OFFERS_DIRECTORY, "job_offers.yaml"])
# JOB_PORTALS = ["nfj","jji","bdj","sj"]
JOB_PORTALS = ["jji", "nfj"]
DATEFORMAT = "%d.%m.%Y"
TODAY = str(datetime.now().strftime(DATEFORMAT))


def load_yaml(filepath: str) -> List[Dict[Any, Any]]:
    """
    Loads the yaml file, e.g.: load existing offers/job_offers.yaml
    """
    with open(file=filepath, mode="r", encoding="utf-8") as old_file:
        return load(stream=old_file, Loader=SafeLoader)


def save_yaml(filepath: str, content: Dict[Any, Any]) -> None:
    """
    Saves content as yaml, e.g.: saving new offers to offers/job_offers.yaml
    """
    # Enable PyYAML support for OrderedDict
    add_representer(
        OrderedDict,
        lambda dumper, data: dumper.represent_dict(
            getattr(data, "viewitems" if version_info < (3,) else "items")()
        ),
        Dumper=SafeDumper,
    )
    with open(file=filepath, mode="w", encoding="utf-8") as new_file:
        safe_dump(data=content, stream=new_file, default_flow_style=False)


def check_if_f_exists_else_empty_dict(filepath: str) -> List[Dict[Any, Any]]:
    """
    Checks whether filepath, e.g.: offers/job_offers.yaml, exists, if not, returns empty dict.
    """
    res = path.isfile(filepath)
    if res:
        content = load_yaml(filepath=filepath)
        if content is not None:
            return content
    return {}


def load_per_job_portal(jp_name: str) -> str:
    """
    Fetches content from each job portal, based on jp_name.
    """
    match jp_name:
        case "nfj":
            nfj_jobs = NoFluffJobs()
            nfj_jobs.load_offers()
            return nfj_jobs.content

        case "jji":
            jji_jobs = JustJoinIT()
            jji_jobs.load_offers()
            return jji_jobs.content

        # case "bdj":
        #     bdj_jobs = BullDogJob()
        #     bdj_jobs.load_offers()
        #     return bdj_jobs.content

        # case "sj":
        #     sj_jobs = SolidJobs()
        #     sj_jobs.load_offers()
        #     return sj_jobs.content

    raise TypeError


def prepare_dict(my_dict: dict, date: str) -> Dict:
    """
    Initialize dictionary with today's date
    """
    if date not in my_dict:
        my_dict[date] = {}

    return my_dict


def sort_by_date(dict_of_offers_by_day: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Sorts the provided dictionary into OrderedDict by DATEFORMAT. Sorts into newest -> oldest.
    """
    return OrderedDict(
        reversed(
            sorted(dict_of_offers_by_day.items(), key=lambda x: datetime.strptime(x[0], DATEFORMAT))
        )
    )


if __name__ == "__main__":
    final_dict = check_if_f_exists_else_empty_dict(FINAL_FILE)
    final_dict = prepare_dict(my_dict=final_dict, date=TODAY)
    for job_portal in JOB_PORTALS:
        JP_CONTENT = load_per_job_portal(jp_name=job_portal)
        if JP_CONTENT is not None:
            final_dict[TODAY][job_portal] = JP_CONTENT
        else:
            print(f"Did not receive any content from {job_portal}.")
        print(f"Done searching {job_portal}.")

    final_dict = sort_by_date(dict_of_offers_by_day=final_dict)
    save_yaml(FINAL_FILE, final_dict)
