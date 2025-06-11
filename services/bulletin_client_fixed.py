import requests
import json
from bs4 import BeautifulSoup
import urllib3
import ssl
import os

# Désactiver les avertissements SSL pour les certificats non vérifiés
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BulletinClient:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session = requests.Session()
        
        # Configuration SSL pour gérer les certificats problématiques
        # En production, on peut avoir des problèmes de certificats avec certains sites universitaires
        self.session.verify = self._should_verify_ssl()
        
        # Headers par défaut pour ressembler à un navigateur
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def _should_verify_ssl(self) -> bool:
        """
        Détermine si on doit vérifier les certificats SSL.
        En développement, on peut être plus strict.
        En production, on peut avoir besoin d'être plus permissif pour certains sites universitaires.
        """
        env = os.getenv("ENVIRONMENT", "development")
        
        # En production, désactiver la vérification SSL pour les sites UVSQ
        # car ils ont souvent des problèmes de certificats
        if env == "production":
            return False
        
        # En développement, essayer d'abord avec vérification
        return True

    def login(self):
        """
        Authentification sur le système de bulletins UVSQ.
        Gère les erreurs SSL et de réseau.
        """
        try:
            # 1. Gather the cookies
            url = "https://bulletins.iut-velizy.uvsq.fr/services/data.php?q=dataPremi%C3%A8reConnexion"
            response = self.session.post(url, timeout=10)
            response.raise_for_status()

            # 2. Gather JWT token
            url = "https://cas2.uvsq.fr/cas/login?service=https%3A%2F%2Fbulletins.iut-velizy.uvsq.fr%2Fservices%2FdoAuth.php%3Fhref%3Dhttps%253A%252F%252Fbulletins.iut-velizy.uvsq.fr%252F"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            token_input = soup.find("input", {"name": "execution"})
            
            if not token_input:
                raise ValueError("Token d'authentification non trouvé")
            
            token = token_input["value"]

            # 3. Login
            url = "https://cas2.uvsq.fr/cas/login?service=https%3A%2F%2Fbulletins.iut-velizy.uvsq.fr%2Fservices%2FdoAuth.php%3Fhref%3Dhttps%253A%252F%252Fbulletins.iut-velizy.uvsq.fr%252F"
            payload = {
                "username": self.username,
                "password": self.password,
                "execution": token,
                "_eventId": "submit",
                "geolocation": "",
            }
            response = self.session.post(url, data=payload, timeout=10)
            response.raise_for_status()
            
        except requests.exceptions.SSLError as e:
            # Si erreur SSL, retry sans vérification
            if self.session.verify:
                self.session.verify = False
                return self.login()  # Retry sans vérification SSL
            else:
                raise Exception(f"Erreur SSL persistante: {str(e)}")
        except requests.exceptions.Timeout:
            raise Exception("Timeout lors de la connexion au service UVSQ")
        except requests.exceptions.ConnectionError:
            raise Exception("Erreur de connexion au service UVSQ")
        except Exception as e:
            raise Exception(f"Erreur lors de l'authentification: {str(e)}")

    def fetch_datas(self):
        """
        Récupère les données du bulletin.
        Gère les erreurs SSL et de réseau.
        """
        try:
            url = "https://bulletins.iut-velizy.uvsq.fr/services/data.php?q=dataPremi%C3%A8reConnexion"
            headers = {
                "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            }
            response = self.session.post(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            json_data = response.text.replace("\n", "")
            return json.loads(json_data)
            
        except requests.exceptions.SSLError as e:
            if self.session.verify:
                self.session.verify = False
                return self.fetch_datas()  # Retry sans vérification SSL
            else:
                return {"error": f"Erreur SSL persistante: {str(e)}"}
        except requests.exceptions.Timeout:
            return {"error": "Timeout lors de la récupération des données"}
        except requests.exceptions.ConnectionError:
            return {"error": "Erreur de connexion au service UVSQ"}
        except json.JSONDecodeError:
            return {"error": "Impossible de décoder la réponse JSON"}
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des données: {str(e)}"}

    def fetch_releve(self, semestre):
        """
        Récupère le relevé de notes pour un semestre donné.
        Gère les erreurs SSL et de réseau.
        """
        try:
            url = "https://bulletins.iut-velizy.uvsq.fr/services/data.php"
            params = {"q": "relevéEtudiant", "semestre": semestre}
            headers = {
                "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            }

            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            if response.status_code == 200:
                try:
                    return json.loads(response.text)
                except json.JSONDecodeError:
                    return {"error": "Impossible de décoder la réponse JSON"}
            return {"error": f"Erreur {response.status_code}"}
            
        except requests.exceptions.SSLError as e:
            if self.session.verify:
                self.session.verify = False
                return self.fetch_releve(semestre)  # Retry sans vérification SSL
            else:
                return {"error": f"Erreur SSL persistante: {str(e)}"}
        except requests.exceptions.Timeout:
            return {"error": "Timeout lors de la récupération du relevé"}
        except requests.exceptions.ConnectionError:
            return {"error": "Erreur de connexion au service UVSQ"}
        except Exception as e:
            return {"error": f"Erreur lors de la récupération du relevé: {str(e)}"}
