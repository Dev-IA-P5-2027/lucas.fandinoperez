# train.py 

import mlflow 

import mlflow.sklearn 

import pandas as pd 

import numpy as np 

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor 

from sklearn.linear_model import Ridge 

from sklearn.model_selection import train_test_split 

from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error 

import argparse 

 

# ── Charger et préparer les données ────────────────────────────── 

df = pd.read_csv('data_immobilier.csv') 

X = df.drop('prix', axis=1) 

y = df['prix'] 

X_train, X_test, y_train, y_test = train_test_split( 

    X, y, test_size=0.2, random_state=42 

) 

 

# ── Paramètres configurables via la ligne de commande ──────────── 

parser = argparse.ArgumentParser() 

parser.add_argument('--model',       default='random_forest') 

parser.add_argument('--n_estimators', type=int, default=100) 

parser.add_argument('--max_depth',    type=int, default=10) 

parser.add_argument('--learning_rate', type=float, default=0.1) 

args = parser.parse_args() 

 

# ── Nommer l'expérience MLflow ──────────────────────────────────── 

# Toutes les runs de ce script seront regroupées sous ce nom 

mlflow.set_experiment('prediction-prix-immobilier') 

 

# ── Ouvrir un run MLflow ────────────────────────────────────────── 

# Tout ce qui se passe dans ce bloc 'with' est enregistré 

with mlflow.start_run(): 

 

    # 1. Enregistrer les paramètres (AVANT l'entraînement) 

    #    Les paramètres = tout ce qu'on a décidé avant de lancer le run 

    mlflow.log_param('model_type',    args.model) 

    mlflow.log_param('n_estimators',  args.n_estimators) 

    mlflow.log_param('max_depth',     args.max_depth) 

    mlflow.log_param('learning_rate', args.learning_rate) 

    mlflow.log_param('train_size',    len(X_train)) 

 

    # 2. Choisir et entraîner le modèle 

    if args.model == 'random_forest': 

        model = RandomForestRegressor( 

            n_estimators=args.n_estimators, 

            max_depth=args.max_depth, 

            random_state=42 

        ) 

    elif args.model == 'gradient_boosting': 

        model = GradientBoostingRegressor( 

            n_estimators=args.n_estimators, 

            max_depth=args.max_depth, 

            learning_rate=args.learning_rate, 

            random_state=42 

        ) 

    else: 

        model = Ridge(alpha=args.max_depth) 

 

    model.fit(X_train, y_train) 

 

    # 3. Calculer les métriques (APRÈS l'entraînement) 

    #    Les métriques = tout ce qu'on mesure une fois le modèle entraîné 

    predictions = model.predict(X_test) 

    mae  = mean_absolute_error(y_test, predictions) 

    rmse = np.sqrt(mean_squared_error(y_test, predictions)) 

    r2   = r2_score(y_test, predictions) 

 

    mlflow.log_metric('MAE',  mae) 

    mlflow.log_metric('RMSE', rmse) 

    mlflow.log_metric('R2',   r2) 
    # 4. Générer et enregistrer la feature importance en CSV
    
    try:
        # Extraire les importances (différent selon le modèle)
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importances = np.abs(model.coef_) # Pour Ridge, on prend la valeur absolue des poids
        else:
            importances = None

        if importances is not None:
            # Créer le DataFrame
            feature_names = X.columns
            df_feat = pd.DataFrame({
                'feature': feature_names,
                'importance': importances
            }).sort_values(by='importance', ascending=False)

            # Sauvegarde temporaire et log
            csv_name = "feature_importance.csv"
            df_feat.to_csv(csv_name, index=False)
            mlflow.log_artifact(csv_name)
            
            # Nettoyage du fichier local
            import os
            os.remove(csv_name)
            print("Feature importance enregistrée avec succès.")

    except Exception as e:
        print(f"Impossible de générer la feature importance : {e}")
 

    # 5. Sauvegarder le modèle comme artefact 

    #    MLflow sérialise le modèle ET son environnement Python 

    mlflow.sklearn.log_model(model, name='model') 

 

    print(f'[{args.model}] MAE={mae:.0f}€  RMSE={rmse:.0f}€  R²={r2:.4f}') 

    print(f'Run ID : {mlflow.active_run().info.run_id}') 