# tests_monitoring.py 

import pandas as pd 

from evidently.test_suite import TestSuite 

from evidently.test_preset import DataDriftTestPreset, DataQualityTestPreset 

from evidently.tests import ( 

    TestNumberOfDriftedColumns, 

    TestShareOfDriftedColumns, 

    TestColumnDrift, 

    TestMeanInNSigmas, 

    TestShareOfMissingValues 

) 

 

df_ref  = pd.read_csv('data_reference.csv') 

df_prod = pd.read_csv('data_production.csv') 

 

# ── Suite de tests avec seuils configurables ────────────────────── 

# Chaque test a un critère de succès/échec explicite 

# → Vous décidez à partir de quand c'est un problème 

suite = TestSuite(tests=[ 

 

    # Test 1 : Pas plus de 2 features driftées simultanément 

    # Au-delà, le modèle voit trop de choses inconnues → re-entraînement nécessaire 

    TestNumberOfDriftedColumns(lte=2), 

 

    # Test 2 : Maximum 40% des features peuvent drifter 

    TestShareOfDriftedColumns(lt=0.4), 

 

    # Test 3 : La surface (feature la plus importante) ne doit pas drifter 

    TestColumnDrift(column_name='surface'), 

 

    # Test 4 : Le prix moyen reste dans ±3 écarts-types de la référence 

    # Cela détecte des changements économiques majeurs 

    TestMeanInNSigmas(column_name='prix', n=3), 

 

    # Test 5 : Qualité des données — pas plus de 5% de valeurs manquantes 

    TestShareOfMissingValues(lt=0.05), 

 

]) 

 

suite.run(reference_data=df_ref, current_data=df_prod) 

suite.save_html('reports/tests_monitoring.html') 

 

# Résumé des tests 

resultats = suite.as_dict() 

tests = resultats['tests'] 

 

print('\nRésultats des tests de monitoring :') 

print('=' * 50) 

for test in tests: 

    statut  = '✅ PASS' if test['status'] == 'SUCCESS' else '❌ FAIL' 

    nom     = test['name'] 

    detail  = test.get('description', '') 

    print(f'{statut}  {nom}') 

    if test['status'] != 'SUCCESS': 

        print(f'       → {detail}') 

 

# Code de sortie non-zéro si des tests échouent 

# → Permet l'intégration dans un pipeline CI/CD (GitHub Actions, etc.) 

nb_echecs = sum(1 for t in tests if t['status'] != 'SUCCESS') 

print(f'\n{nb_echecs} test(s) en échec sur {len(tests)}') 

exit(1 if nb_echecs > 0 else 0) 