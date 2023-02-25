from os import makedirs
from requests import get
from time import sleep
from os import makedirs
from re import findall
from datetime import datetime

class nfj:
    NFJ_URL = "https://nofluffjobs.com/pl/praca-zdalna/devops?criteria=employment%3Db2b%20requirement%3DAWS%20salary%3Epln20000m%20%20seniority%3Dmid&page="

    def __init__(self):
        pass

    def load_todays_offers(self, url: str = NFJ_URL):
        """
        Loads all the offers present in the URL
        """
        today = datetime.now().strftime("%d.%m.%Y")
        self.content = []
        page = 1
        while True:
            r = get(url+str(page))
            r = r.content.decode("utf-8")
            job_offers = findall(r'/pl/job[^"]*', r)
            if len(job_offers) > 0:
                [self.content.append({
                        "id": str(findall(r"([\d\w]+(\-[\d\w]+)+)", job)[0][1]).replace('-',''),
                        "job_name": findall(r"([\d\w]+(\-[\d\w]+)+)", job)[0][0],
                        "url": "https://nofluffjobs.com" + job,
                    })
                    for job in job_offers]
                page+=1
            else:
                break
