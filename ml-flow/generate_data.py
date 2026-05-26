# generate_data.py 

import pandas as pd 

import numpy as np 

np.random.seed(42) 

n = 1000 

 

# Générer des features réalistes 

surface   = np.random.randint(20, 200, n)          # m² 

chambres  = np.random.randint(1, 6, n)             # nombre de pièces 

distance  = np.random.uniform(1, 30, n)            # km du centre-ville 

annee     = np.random.randint(1960, 2023, n)       # année de construction 

 

# Prix : relation linéaire + bruit réaliste 

prix = (surface * 3200 

        + chambres * 15000 

        - distance * 8000 

        + (annee - 1960) * 500 

        + np.random.normal(0, 20000, n)) 

 

df = pd.DataFrame({ 

    'surface': surface, 

    'chambres': chambres, 

    'distance_centre': distance, 

    'annee_construction': annee, 

    'prix': prix.astype(int) 

}) 

 

df.to_csv('data_immobilier.csv', index=False) 

print(f'Dataset généré : {len(df)} lignes') 

print(df.describe().round(0)) 
