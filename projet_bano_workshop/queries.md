# Requêtes Kibana Dev Tools - bano-25

## 1. Recherche d'adresse sur Kibana (dev tools)

```
GET bano-25/_search?search_type=dfs_query_then_fetch
{
  "size": 1,
  "query": {
    "bool": {
      "should": [
        { "match": { "numero": "23" } },
        { "match": { "rue": "rue lanchy" } },
        { "match": { "commune": "besançon" } }
      ]
    }
  }
}
```

- Score =  15,98 pour `23 Rue Narcisse Lanchy, Besançon`.
- Limite : `besancon` sans cédille ne matche pas (analyzer standard, accents conservés). 

## 2. Recherche géo (rayon 200m + tri par distance)

```
GET bano-25/_search
{
  "size": 5,
  "query": {
    "bool": {
      "filter": {
        "geo_distance": {
          "distance": "200m",
          "location": { "lat": 47.245912, "lon": 6.034779 }
        }
      }
    }
  },
  "sort": [
    {
      "_geo_distance": {
        "location": { "lat": 47.245912, "lon": 6.034779 },
        "order": "asc",
        "unit": "m"
      }
    }
  ]
}
```

- `geo_distance` en `filter` : pas de score, mis en cache.
- 120 adresses dans les 200m autour du point.

## Comparatif : Dev Tools vs script Python (`queries.py`)

| Critère | Kibana Dev Tools | Python (`queries.py`) |
|---|---|---|
| Itération / tests rapides | Très rapide, autocomplétion | Plus lent (relancer le script) |
| Lecture de la réponse | JSON brut complet | Affichage formaté (`afficher()`) |
| Reproductibilité | Faible (copier-coller) | Bonne (fichier versionné) |
| Paramétrage (rayon, point...) | Manuel | Fonctions avec paramètres |
| Mesure de perf (`took`) | Visible dans la réponse | Comparable en boucle / automatisable |
| Usage recommandé | Explorer, valider une requête | Livrable GitHub, comparaisons |
