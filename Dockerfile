FROM python:3.11-slim

# Définir le dossier de travail
WORKDIR /app

# Copier les fichiers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exposer le port interne
EXPOSE 8000

# Lancer Uvicorn (toujours sur 0.0.0.0 pour Docker)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
