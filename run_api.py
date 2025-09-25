import uvicorn

if __name__ == "__main__":
    # Configuration du serveur
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Activer le rechargement automatique
        reload_excludes=["__pycache__"],  # Exclure les dossiers __pycache__
    )
    
    print("API démarrée")
