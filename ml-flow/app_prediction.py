# app_prediction.py — Simule une application qui utilise le modèle en production 

import mlflow.sklearn 

import pandas as pd 

 

MODEL_NAME = 'GBR' 

 

# Charger toujours le modèle en Production, quel que soit son numéro de version 

# Quand vous déployez une v2, cette ligne continue de fonctionner sans modification 

model = mlflow.sklearn.load_model(f'models:/{MODEL_NAME}/Production') 

 

def predire_prix(surface, chambres, distance, annee): 

    """Prédit le prix d'un bien immobilier.""" 

    data = pd.DataFrame([{ 

        'surface': surface, 

        'chambres': chambres, 

        'distance_centre': distance, 

        'annee_construction': annee 

    }]) 

    return model.predict(data)[0] 

 

# Test de l'application 

exemples = [ 

    (50,  2, 3.0, 2010, 'Studio proche centre'), 

    (90,  4, 12.0, 1985, 'Grande maison en périphérie'), 

    (35,  1, 1.5, 2020, 'Studio neuf hyper-centre'), 

] 

 

print('Prédictions du modèle en Production :') 

print('-' * 50) 

for surface, ch, dist, annee, desc in exemples: 

    prix = predire_prix(surface, ch, dist, annee) 

    print(f'{desc:35s} → {prix:>10,.0f} €') 