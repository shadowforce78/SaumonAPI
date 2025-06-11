"""
Script de test pour vérifier la configuration CSP et Swagger UI
"""
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_swagger_docs():
    """Test que la page docs est accessible"""
    response = client.get("/docs")
    print(f"Status code /docs: {response.status_code}")
    
    # Vérifier les en-têtes CSP
    csp_header = response.headers.get("Content-Security-Policy")
    print(f"CSP Header: {csp_header}")
    
    # Vérifier que la réponse contient du HTML
    if response.status_code == 200:
        print("✅ Swagger UI docs accessible")
        if "cdn.jsdelivr.net" in csp_header:
            print("✅ CSP autorise cdn.jsdelivr.net")
        else:
            print("❌ CSP ne contient pas cdn.jsdelivr.net")
    else:
        print("❌ Swagger UI docs non accessible")

def test_openapi_json():
    """Test que le schéma OpenAPI est accessible"""
    response = client.get("/openapi.json")
    print(f"Status code /openapi.json: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ OpenAPI schema accessible")
    else:
        print("❌ OpenAPI schema non accessible")

def test_api_endpoint():
    """Test qu'un endpoint normal fonctionne"""
    response = client.get("/")
    print(f"Status code /: {response.status_code}")
    
    # Vérifier les en-têtes CSP pour un endpoint normal
    csp_header = response.headers.get("Content-Security-Policy")
    print(f"CSP Header endpoint normal: {csp_header}")
    
    if response.status_code == 200:
        print("✅ Endpoint principal accessible")
    else:
        print("❌ Endpoint principal non accessible")

if __name__ == "__main__":
    print("=== Test de la configuration CSP et Swagger UI ===\n")
    test_swagger_docs()
    print()
    test_openapi_json()
    print()
    test_api_endpoint()
    print("\n=== Fin des tests ===")
