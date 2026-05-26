# Image de base officielle Python 

# 'slim' = version allégée sans outils inutiles → image plus petite 

FROM python:3.11-slim 

 

# Définir le répertoire de travail dans le conteneur 

# Toutes les commandes suivantes s'exécuteront depuis /app 

WORKDIR /app 

 

# ── ÉTAPE CRITIQUE : copier requirements.txt EN PREMIER ── 

# Séparer cette copie du reste du code est une optimisation du cache Docker 

COPY requirements.txt . 

RUN pip install --no-cache-dir -r requirements.txt 

 

# Copier le code source APRÈS les dépendances 

COPY app.py . 

 

# Documentation : indique quel port l'application utilise 

# N'ouvre PAS vraiment le port — c'est informatif (docker run -p le fait) 

EXPOSE 8000 

 

# Commande lancée au démarrage du conteneur 

# uvicorn  : le serveur web qui fait tourner FastAPI 

# app:app  : fichier app.py, objet app 

# --host 0.0.0.0 : écouter sur toutes les interfaces réseau du conteneur 

#                  (sinon le conteneur serait inaccessible de l'extérieur) 

# --port 8000     : port d'écoute 

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"] 