from fastapi import FastAPI
from routers.uvsq.edt import router as uvsq_edt_router
from routers.uvsq.bulletin import router as uvsq_bulletin_router
from routers.scans.routes import router as scans_router

# Création de l'application FastAPI
app = FastAPI(
    title="SaumonAPI",
    description="API pour récupérer des informations sur les scans et l'UVSQ",
    version="1.0.0",
)


# Page d'accueil
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur SaumonAPI !"}


# Inclusion des routers
app.include_router(uvsq_edt_router)
app.include_router(uvsq_bulletin_router)
app.include_router(scans_router)
