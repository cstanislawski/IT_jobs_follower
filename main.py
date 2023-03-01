"""
Module for tracking offers on sites specified in config.yaml.
"""

from datetime import datetime
from os import path
from typing import List, Dict, Any
from yaml import load, safe_dump, SafeLoader  # pylint: disable=E0401
from job_portals.nfj import NoFluffJobs
from job_portals.jji import JustJoinIT

# from job_portals.bdj import BullDogJob
# from job_portals.sj import SolidJobs


OFFERS_DIRECTORY = "offers/"
FINAL_FILE = "".join([OFFERS_DIRECTORY, "job_offers.yaml"])
# JOB_PORTALS = ["nfj","jji","bdj","sj"]
# JOB_PORTALS = ["nfj"]
JOB_PORTALS = ["nfj", "jji"]
TODAY = str(datetime.now().strftime("%d.%m.%Y"))


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
    with open(file=filepath, mode="w", encoding="utf-8") as new_file:
        safe_dump(data=content, stream=new_file)


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


def prepare_dict(my_dict: dict, date: str) -> dict:
    """
    Initialize dictionary with today's date
    """
    if date not in my_dict:
        my_dict[date] = {}

    return my_dict


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

    save_yaml(FINAL_FILE, final_dict)
