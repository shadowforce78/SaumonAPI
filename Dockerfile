FROM python:3.11-slim

# Définir le dossier de travail
WORKDIR /app

# Copier les fichiers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# ATTENTION : copie du fichier .env (pratique en dev, déconseillée en prod si le build est fait dans un CI)
# Pour la production préférer :
#   docker run -e GEMINI=xxx ...  OU  docker compose avec env_file / secrets
# Si vous ne voulez PAS embarquer .env dans l'image finale, commentez la ligne suivante :
COPY .env ./.env

# Exposer le port interne
EXPOSE 8000

# Lancer Uvicorn (toujours sur 0.0.0.0 pour Docker)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
