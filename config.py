import os
from typing import List

class Settings:
    """Configuration de l'application"""
    
    # Configuration CORS
    CORS_ORIGINS: List[str] = [
        # Environnement de développement
        "http://localhost:3000",    # React
        "http://localhost:5173",    # Vite
        "http://localhost:8080",    # Vue
        "http://localhost:4200",    # Angular
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:4200",
    ]
      # Environnement de production - domaines autorisés
    PRODUCTION_ORIGINS: List[str] = [
        "https://saumondeluxe.com",
        "https://www.saumondeluxe.com",
        "https://api.saumondeluxe.com",
    ]
      # Configuration CSP
    CSP_POLICY = (
        "default-src 'self' https://saumondeluxe.com https://api.saumondeluxe.com; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://saumondeluxe.com; "
        "style-src 'self' 'unsafe-inline' https://saumondeluxe.com; "
        "img-src 'self' data: https: http: https://saumondeluxe.com https://api.saumondeluxe.com; "
        "font-src 'self' data: https://saumondeluxe.com; "
        "connect-src 'self' https: http: https://saumondeluxe.com https://api.saumondeluxe.com; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self' https://saumondeluxe.com"
    )
      # Configuration des hôtes de confiance
    TRUSTED_HOSTS: List[str] = [
        "localhost",
        "127.0.0.1",
        "saumondeluxe.com",
        "www.saumondeluxe.com",
        "api.saumondeluxe.com",
    ]
    
    @classmethod
    def get_cors_origins(cls) -> List[str]:
        """Retourne la liste des origines CORS autorisées"""
        origins = cls.CORS_ORIGINS.copy()
        
        # En production, ajoutez les domaines de production
        env = os.getenv("ENVIRONMENT", "development")
        if env == "production":
            origins.extend(cls.PRODUCTION_ORIGINS)
        
        # Possibilité d'ajouter des origines via variable d'environnement
        extra_origins = os.getenv("CORS_ORIGINS", "")
        if extra_origins:
            origins.extend(extra_origins.split(","))
        
        return origins

settings = Settings()
