# app.py 

from fastapi import FastAPI, HTTPException 

import random 

 

 

# Le titre et la version apparaîtront automatiquement dans /docs 

app = FastAPI(title="API Météo", version="1.0") 

 

# Données météo fictives stockées en mémoire 

DONNEES = { 

    "paris":     {"temperature": 18, "condition": "Nuageux"}, 

    "marseille": {"temperature": 26, "condition": "Ensoleillé"}, 

    "lyon":      {"temperature": 21, "condition": "Partiellement nuageux"}, 

    "bordeaux":  {"temperature": 23, "condition": "Ensoleillé"}, 
    "besancon": {"temperature": 20, "condition": "Couvert"},}



 

# Route racine : retourne des infos sur l'API 

@app.get("/") 

def accueil(): 

    return {"api": "Météo", "version": "1.0", 

            "routes": ["/villes", "/meteo/{ville}", "/meteo/aleatoire"]} 

 

# Route listant toutes les villes disponibles 

@app.get("/villes") 

def villes(): 

    return {"villes": list(DONNEES.keys())} 

 

# Retourne la météo d'une ville choisie aléatoirement

@app.get("/meteo/aleatoire") 

def meteo_aleatoire():
    # 1. On récupère la liste de tous les noms de villes
    villes_disponibles = list(DONNEES.keys())
    
    # 2. On choisit une ville au hasard dans cette liste
    ville_choisie = random.choice(villes_disponibles)
    
    # 3. On appelle simplement la logique de la fonction météo existante
    # ou on retourne directement les données
    return meteo(ville_choisie)


# Route retournant la météo d'une ville 

# {ville} est un paramètre d'URL récupéré directement par FastAPI 

@app.get("/meteo/{ville}") 

def meteo(ville: str): 

    ville = ville.lower() 

    if ville not in DONNEES: 

        # HTTPException génère automatiquement une réponse 404 JSON 

        raise HTTPException(status_code=404, 

                           detail=f"Ville '{ville}' introuvable") 

    data = DONNEES[ville].copy() 

    data["temperature"] += random.randint(-2, 2)  # variation réaliste 

    data["ville"] = ville.capitalize() 

    return data 


    