from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request
from routers.uvsq.edt import router as uvsq_edt_router
from routers.uvsq.bulletin import router as uvsq_bulletin_router
from routers.scans.routes import router as scans_router
from config import settings
import os

# Création de l'application FastAPI
app = FastAPI(
    title="SaumonAPI",
    description="API pour récupérer des informations sur les scans et l'UVSQ",
    version="1.0.0",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRFToken",
        "Cache-Control",
        "Pragma",
    ],
    expose_headers=["X-Total-Count", "X-Page-Count"],
)

# Middleware pour les en-têtes de sécurité (CSP et autres)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # CSP simplifiée pour la documentation Swagger
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
        # CSP très permissive pour Swagger UI uniquement
        response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net data:; img-src * data:;"
    else:
        # CSP normale pour les autres endpoints
        response.headers["Content-Security-Policy"] = settings.CSP_POLICY
    
    # Autres en-têtes de sécurité
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    # En production, ajoutez HSTS
    if os.getenv("ENVIRONMENT") == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

# Middleware pour les hôtes de confiance (activé en production)
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=settings.TRUSTED_HOSTS
    )


# Page d'accueil
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur SaumonAPI !"}


# Endpoint de test CORS
@app.get("/test-cors")
def test_cors():
    """Endpoint pour tester la configuration CORS"""
    return {
        "message": "CORS est configuré correctement",
        "cors_origins": settings.get_cors_origins(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": "2025-06-09"
    }


@app.options("/{full_path:path}")
def options_handler(full_path: str):
    """Gestion explicite des requêtes OPTIONS pour CORS"""
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
        }
    )


# Inclusion des routers
app.include_router(uvsq_edt_router)
app.include_router(uvsq_bulletin_router)
app.include_router(scans_router)
