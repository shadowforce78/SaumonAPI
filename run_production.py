import uvicorn
import os

if __name__ == "__main__":
    # Configuration pour la production
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":        # Configuration optimisée pour la production
        uvicorn.run(
            "app:app",
            host="0.0.0.0",  # Écoute sur toutes les interfaces
            port=int(os.getenv("PORT", 8000)),  # Port par défaut 8000 pour la production
            workers=int(os.getenv("WORKERS", 4)),  # Plusieurs workers pour la production
            access_log=True,
            log_level="info",
        )
    else:
        # Configuration pour le développement
        uvicorn.run(
            "app:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            reload_excludes=["__pycache__"],
            log_level="debug",
        )
    
    print(f"API démarrée en mode {environment}")
