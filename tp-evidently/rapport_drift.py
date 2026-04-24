# rapport_drift.py 

import pandas as pd 

from evidently.report import Report 

from evidently.metric_preset import DataDriftPreset, DataQualityPreset 

from evidently.metrics import ColumnDriftMetric 

import os 

 
 

os.makedirs('reports', exist_ok=True) 

 

# Charger les deux datasets 

df_ref  = pd.read_csv('data_reference.csv') 

df_prod = pd.read_csv('data_production.csv') 

 

# ── Rapport de Data Drift ───────────────────────────────────────── 

# DataDriftPreset analyse automatiquement toutes les colonnes 

# Il choisit le bon test statistique selon le type de la colonne : 

# - Kolmogorov-Smirnov pour les variables continues (surface, prix...) 

# - Chi-carré pour les variables catégorielles 

rapport_drift = Report(metrics=[ 

    DataDriftPreset(),        # Vue d'ensemble du drift sur toutes les features 

    DataQualityPreset(),      # Qualité des données (valeurs manquantes, doublons...) 

    # Focus sur des colonnes spécifiques 

    ColumnDriftMetric(column_name='surface'), 

    ColumnDriftMetric(column_name='prix'), 

    ColumnDriftMetric(column_name='annee_construction'), 

]) 

 

# Comparer : reference = données d'entraînement, current = données de prod 

rapport_drift.run(reference_data=df_ref, current_data=df_prod) 

 

# Sauvegarder le rapport HTML interactif 

rapport_drift.save_html('reports/rapport_drift.html') 

print('Rapport généré : reports/rapport_drift.html') 

 

# Accéder aux résultats programmatiquement (utile pour les alertes) 

resultats = rapport_drift.as_dict() 

drift_global = resultats['metrics'][0]['result'] 

print(f"\nNombre de features : {drift_global['number_of_columns']}") 

print(f"Features driftées  : {drift_global['number_of_drifted_columns']}") 

print(f"Part de drift      : {drift_global['share_of_drifted_columns']:.0%}") 