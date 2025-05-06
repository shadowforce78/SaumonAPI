import requests
import json
from bs4 import BeautifulSoup


class BulletinClient:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session = requests.Session()

    def login(self):
        # 1. Gather the cookies
        url = "https://bulletins.iut-velizy.uvsq.fr/services/data.php?q=dataPremi%C3%A8reConnexion"
        self.session.post(url)

        # 2. Gather JWT token
        url = "https://cas2.uvsq.fr/cas/login?service=https%3A%2F%2Fbulletins.iut-velizy.uvsq.fr%2Fservices%2FdoAuth.php%3Fhref%3Dhttps%253A%252F%252Fbulletins.iut-velizy.uvsq.fr%252F"
        response = self.session.get(url)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        token = soup.find("input", {"name": "execution"})["value"]

        # 3. Login
        url = "https://cas2.uvsq.fr/cas/login?service=https%3A%2F%2Fbulletins.iut-velizy.uvsq.fr%2Fservices%2FdoAuth.php%3Fhref%3Dhttps%253A%252F%252Fbulletins.iut-velizy.uvsq.fr%252F"
        payload = {
            "username": self.username,
            "password": self.password,
            "execution": token,
            "_eventId": "submit",
            "geolocation": "",
        }
        self.session.post(url, data=payload)

    def fetch_datas(self):
        url = "https://bulletins.iut-velizy.uvsq.fr/services/data.php?q=dataPremi%C3%A8reConnexion"
        headers = {
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        }
        response = self.session.post(url, headers=headers)
        json_data = response.text.replace("\n", "")
        return json.loads(json_data)

    def fetch_releve(self, semestre):
        url = "https://bulletins.iut-velizy.uvsq.fr/services/data.php"
        params = {"q": "relevéEtudiant", "semestre": semestre}
        headers = {
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        }

        response = self.session.get(url, params=params, headers=headers)
        if response.status_code == 200:
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                return {"error": "Impossible de décoder la réponse JSON"}
        return {"error": f"Erreur {response.status_code}"}