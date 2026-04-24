import mlflow 

import mlflow.sklearn 

import pandas as pd 

 

# Remplacer par le Run ID affiché dans l'interface (ex: 'abc123def456') 

RUN_ID = '88618cc3279f48b69a1fbaa6f70b07c7' 

 

# Charger le modèle directement depuis MLflow 

# MLflow sait où trouver le fichier, quelle version de scikit-learn était utilisée, etc. 

model = mlflow.sklearn.load_model(f'runs:/{RUN_ID}/model') 

 

# Faire une prédiction sur un appartement fictif 

appartement = pd.DataFrame([{ 

    'surface': 75, 

    'chambres': 3, 

    'distance_centre': 5.2, 

    'annee_construction': 2005 

}]) 

 

prix_predit = model.predict(appartement)[0] 

print(f'Prix prédit : {prix_predit:,.0f} €') 