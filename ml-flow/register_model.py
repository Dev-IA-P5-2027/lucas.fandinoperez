# register_model.py 

import mlflow 

import mlflow.sklearn 

from mlflow.tracking import MlflowClient 

 

# Le nom sous lequel le modèle sera connu dans le Registry 

MODEL_NAME = 'GBR' 

 

# Remplacer par le Run ID du meilleur run (visible dans l'UI) 

RUN_ID = '82df3d2d98c94d8e96e4fc1b7d283ac7'

 

# Enregistrer le modèle du run dans le Registry 

# MLflow crée automatiquement la version 1, 2, 3... à chaque enregistrement 

result = mlflow.register_model( 

    model_uri=f'runs:/{RUN_ID}/model', 

    name=MODEL_NAME 

) 

 

print(f'Modèle enregistré : {MODEL_NAME} version {result.version}') 

 

# ── Ajouter une description ───────────────────────────────────── 

client = MlflowClient() 

client.update_model_version( 

    name=MODEL_NAME, 

    version=result.version, 

    description='Model GradientBoostingRegressor' 

) 

 

# ── Passer le modèle en Staging ────────────────────────────────── 

# Staging = modèle validé techniquement, en attente de validation métier 

client.transition_model_version_stage( 

    name=MODEL_NAME, 

    version=result.version, 

    stage='Staging' 

) 

print(f'Modèle v{result.version} → Staging') 