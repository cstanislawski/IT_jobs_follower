"""
Module for tracking offers on sites specified in config.yaml.
"""

from datetime import datetime
from os import path
from yaml import load, safe_dump, SafeLoader  # pylint: disable=E0401
from job_portals.nfj import NoFluffJobs
from job_portals.jjt import JustJoinIT
from job_portals.bdj import BullDogJob
from job_portals.sj import SolidJobs


OFFERS_DIRECTORY = "offers/"
FINAL_FILE = "".join([OFFERS_DIRECTORY, "job_offers.yaml"])
# job_portals = ["nfj", "jjt", "bdj", "sj"]
JOB_PORTALS = ["nfj"]
TODAY = str(datetime.now().strftime("%d.%m.%Y"))


def load_yaml(filepath: str):
    """
    Loads the yaml file, e.g.: load existing offers/job_offers.yaml
    """
    with open(file=filepath, mode="r", encoding="utf-8") as old_file:
        return load(stream=old_file, Loader=SafeLoader)


def save_yaml(filepath: str, content: list[dict]):
    """
    Saves content as yaml, e.g.: saving new offers to offers/job_offers.yaml
    """
    with open(file=filepath, mode="w", encoding="utf-8") as new_file:
        safe_dump(data=content, stream=new_file)


def check_if_f_exists_else_empty_dict(filepath: str):
    """
    Checks whether filepath, e.g.: offers/job_offers.yaml, exists, if not, returns empty dict.
    """
    res = path.isfile(filepath)
    if res:
        content = load_yaml(filepath=filepath)
        if content is not None:
            return content
    return {}


def load_per_job_portal(jp_name: str):
    """
    Fetches content from each job portal, based on jp_name.
    """
    match jp_name:
        case "nfj":
            jobs = NoFluffJobs()
            jobs.load_offers()
            return jobs.content

        case "jjt":
            jobs = JustJoinIT()
            jobs.load_offers()
            return jobs.content

        case "bdj":
            jobs = BullDogJob()
            jobs.load_offers()
            return jobs.content

        case "sj":
            jobs = SolidJobs()
            jobs.load_offers()
            return jobs.content

    return None


def prepare_dict(my_dict: dict, date):
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

    save_yaml(FINAL_FILE, final_dict)
