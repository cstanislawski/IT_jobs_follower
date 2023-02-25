from os import makedirs
from requests import get
from time import sleep
from os import makedirs
from re import findall
from datetime import datetime

class nfj:
    NFJ_URL = "https://nofluffjobs.com/pl/praca-zdalna/devops?criteria=employment%3Db2b%20requirement%3DAWS%20salary%3Epln20000m%20%20seniority%3Dmid&page=1"

    def __init__(self):
        pass

    def load(self, content: list[dict] = None):
        today = datetime.now().strftime("%d.%m.%Y")
        r = get(self.NFJ_URL)
        r = r.content.decode("utf-8")
        job_offers = findall(r'/pl/job[^"]*', r)
        self.content = [
            {
                "id": str(findall(r"([\d\w]+(\-[\d\w]+)+)", job)[0][1]).replace('-',''),
                "job_name": findall(r"([\d\w]+(\-[\d\w]+)+)", job)[0][0],
                "url": "https://nofluffjobs.com" + job,
            }
            for job in job_offers
        ]

        if content:
            for single_dict in content:
                if single_dict not in self.content:
                    self.content.append(single_dict)
                    print('Appended:')
                    print(single_dict)