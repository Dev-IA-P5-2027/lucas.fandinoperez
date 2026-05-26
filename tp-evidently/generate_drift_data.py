# generate_drift_data.py 

import pandas as pd 

import numpy as np 

 

np.random.seed(42) 

 

def generer_dataset(n, drift=False): 

    """ 

    Génère un dataset immobilier. 

    Si drift=True, simule un marché qui a évolué : 

    - Prix au m² en hausse (inflation immobilière) 

    - Tendance vers des biens plus petits (urbanisation) 

    - Moins de biens anciens (rénovation du parc) 

    """ 

    if drift: 

        # Distribution driftée : appartements plus petits, plus récents, plus chers 

        surface  = np.random.randint(20, 120, n)          # plus petit qu'avant 

        chambres = np.clip(np.random.poisson(2.0, n), 1, 5)  # moins de grandes familles 

        distance = np.random.uniform(1, 20, n)             # plus proche du centre 

        annee    = np.random.randint(1990, 2024, n)        # parc plus récent 

        # Prix au m² 40% plus élevé (inflation) 

        prix = (surface * 4500 + chambres * 18000 

                - distance * 9000 + (annee - 1960) * 600 

                + np.random.normal(0, 25000, n)) 

    else: 

        # Distribution de référence (données d'entraînement 2022) 

        surface  = np.random.randint(20, 200, n) 

        chambres = np.random.randint(1, 6, n) 

        distance = np.random.uniform(1, 30, n) 

        annee    = np.random.randint(1960, 2023, n) 

        prix = (surface * 3200 + chambres * 15000 

                - distance * 8000 + (annee - 1960) * 500 

                + np.random.normal(0, 20000, n)) 

 

    return pd.DataFrame({ 

        'surface': surface, 

        'chambres': chambres, 

        'distance_centre': distance.round(1), 

        'annee_construction': annee, 

        'prix': prix.astype(int) 

    }) 

 

# Données de référence : ce sur quoi le modèle a été entraîné 

df_reference = generer_dataset(1000, drift=False) 

df_reference.to_csv('data_reference.csv', index=False) 

print('Référence générée :', df_reference.shape) 

print(df_reference[['surface', 'prix']].describe().round(0)) 

 

# Données de production : ce qui arrive 18 mois plus tard 

df_production = generer_dataset(500, drift=True) 

df_production.to_csv('data_production.csv', index=False) 

print('\nProduction (driftée) générée :', df_production.shape) 

print(df_production[['surface', 'prix']].describe().round(0))