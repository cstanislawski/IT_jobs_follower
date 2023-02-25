from requests import get
from re import findall
from time import sleep
from datetime import datetime
from os import makedirs, path
from job_portals.nfj import nfj
from job_portals.jjt import jjt
from job_portals.bdj import bdj
from job_portals.sj import sj
import yaml

OFFERS_DIRECTORY = "offers/"
FINAL_FILE = "".join([OFFERS_DIRECTORY, "job_offers.yaml"])
# job_portals = ["nfj", "jjt", "bdj", "sj"]
job_portals = ["nfj"]


def load_yaml(filepath: str):
    with open(file=filepath, mode="r") as f:
        return yaml.load(stream=f, Loader=yaml.SafeLoader)


def save_yaml(filepath: str, content: list[dict]):
    with open(file=filepath, mode="w") as f:
        yaml.safe_dump(data=content, stream=f)


def check_if_f_exists_else_empty_dict(filepath: str):
    res = path.isfile(filepath)
    if res:
        content = load_yaml(filepath=filepath)
        if content != None:
            return content
    return {}


def load_per_job_portal(jp_name: str, content: list[dict] = None):
    match jp_name:
        case "nfj":
            jobs = nfj()
            jobs.load_todays_offers()
            return jobs.content

        case "jjt":
            jobs = jjt()
            if content:
                jobs.load(content)
            else:
                jobs.load()
            return jobs.content

        case "bdj":
            jobs = bdj()
            if content:
                jobs.load(content)
            else:
                jobs.load()
            return jobs.content

        case "sj":
            jobs = sj()
            if content:
                jobs.load(content)
            else:
                jobs.load()
            return jobs.content

    return None


def prepare_dict(my_dict: dict, date):
    if date not in my_dict:
        my_dict[date] = {}

    return my_dict


if __name__ == "__main__":
    today = str(datetime.now().strftime("%d.%m.%Y"))
    final_dict = check_if_f_exists_else_empty_dict(FINAL_FILE)
    final_dict = prepare_dict(my_dict=final_dict, date=today)
    for job_portal in job_portals:
        jp_content = load_per_job_portal(jp_name=job_portal)
        if jp_content != None:
            final_dict[today][job_portal] = jp_content
        else:
            print(f"Did not receive any content from {job_portal}.")

    save_yaml(FINAL_FILE, final_dict)
