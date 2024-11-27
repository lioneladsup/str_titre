# Utiliser une image officielle de Python 3.10
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers nécessaires dans le conteneur
COPY . /app

# Mettre à jour pip et setuptools avant d'installer les dépendances
RUN pip install --upgrade pip setuptools

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port 8501 (port par défaut pour Streamlit)
EXPOSE 8501

# Commande pour démarrer l'application Streamlit
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.enableCORS", "false"]

