# monitoring_pipeline.py — Simule une semaine de monitoring en production 

import pandas as pd 

import numpy as np 

import mlflow.sklearn 

from evidently.report import Report 

from evidently.metric_preset import DataDriftPreset 

from evidently.test_suite import TestSuite 

from evidently.tests import TestShareOfDriftedColumns, TestMeanInNSigmas 

from datetime import datetime 

import os 

 

os.makedirs('reports', exist_ok=True)



mlflow.set_tracking_uri('sqlite:////Users/Licas/Desktop/ml-flow/mlflow.db')



MODEL_NAME = 'GBR'

 

def run_monitoring(semaine: int, use_drift: bool): 

    """Simule le monitoring d'une semaine de production.""" 

    print(f'\n=== Semaine {semaine} ===  (drift={use_drift})') 

 

    # Charger le modèle de production 

    model = mlflow.sklearn.load_model(f'models:/{MODEL_NAME}/Production') 

 

    # Données de référence (entraînement) 

    df_ref = pd.read_csv('data_reference.csv') 

    features = ['surface', 'chambres', 'distance_centre', 'annee_construction'] 

 

    # Simuler les données de la semaine 

    np.random.seed(semaine) 

    n = 100 

    if use_drift: 

        df_current = pd.DataFrame({ 

            'surface':              np.random.randint(20, 110, n), 

            'chambres':             np.random.randint(1, 4, n), 

            'distance_centre':      np.random.uniform(1, 15, n).round(1), 

            'annee_construction':   np.random.randint(1995, 2024, n), 

        }) 

    else: 

        df_current = pd.DataFrame({ 

            'surface':              np.random.randint(20, 200, n), 

            'chambres':             np.random.randint(1, 6, n), 

            'distance_centre':      np.random.uniform(1, 30, n).round(1), 

            'annee_construction':   np.random.randint(1960, 2023, n), 

        }) 

 

    # Faire les prédictions et les ajouter au dataset 

    df_current['prix'] = model.predict(df_current[features]).astype(int) 

 

    # Tests de monitoring 

    suite = TestSuite(tests=[ 

        TestShareOfDriftedColumns(lt=0.3), 

        TestMeanInNSigmas(column_name='prix'),

    ]) 

    suite.run(reference_data=df_ref, current_data=df_current) 

 

    # Rapport détaillé 

    rapport = Report(metrics=[DataDriftPreset()]) 

    rapport.run(reference_data=df_ref, current_data=df_current) 

    rapport.save_html(f'reports/semaine_{semaine:02d}.html') 

 

    # Analyser les résultats 

    tests_results = suite.as_dict()['tests'] 

    nb_echecs = sum(1 for t in tests_results if t['status'] != 'SUCCESS') 

 

    if nb_echecs > 0: 

        print(f'⚠️  ALERTE : {nb_echecs} test(s) en échec !') 

        print(f'   → Rapport : reports/semaine_{semaine:02d}.html') 

        print('   → Action recommandée : analyser le drift et planifier un ré-entraînement') 

    else: 

        print(f'✅  Tous les tests passent — modèle stable') 

 

    return nb_echecs 

 

# Simuler 4 semaines : les 2 premières normales, les 2 suivantes avec drift 

resultats = [] 

for semaine in range(1, 5): 

    use_drift = semaine > 2  # drift à partir de la semaine 3 

    echecs = run_monitoring(semaine, use_drift) 

    resultats.append({'semaine': semaine, 'alertes': echecs}) 

 

print('\n=== Résumé des 4 semaines ===') 

for r in resultats: 

    statut = '🔴 ALERTE' if r['alertes'] > 0 else '🟢 OK' 

    print(f"  Semaine {r['semaine']} : {statut}") 