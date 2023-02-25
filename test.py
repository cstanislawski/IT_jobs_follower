from requests import get

NFJ_URL = "https://nofluffjobs.com/pl/praca-zdalna/devops?criteria=employment%3Db2b%20requirement%3DAWS%20salary%3Epln20000m%20%20seniority%3Dmid&page=3"

if __name__ == "__main__":
    r = get(NFJ_URL)
    print(r.is_redirect)