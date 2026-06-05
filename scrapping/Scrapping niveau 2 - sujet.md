# Extraires les données d'un site par Scrapping (niveau 2)

***Extraction des titres d'un site d'actualité pour une mise quotidienne en base de données***

### Contexte du projet
Votre entreprise vous demande de disposer, en base de données, des titres des articles du site [20 minutes][site].
(voir [l'image][imageSite] jointe)
![Vue du site][imageSite]


Chaque jour, un script ira collecter ces titres, ainsi que leur catégorie, et les placera en base de données, avec un horodatage.

On doit pouvoir ainsi, par exemple, pouvoir récupérer tous les titres des articles concernant "Roland Garros", au mois de mai 2025.

1. Rechercher l'organisation HTML du site internet concerné, et notamment les noms et type de balise permettant de repérer les titres et catégories de articles.

2. Ecrire un script python qui récupère ces informations par scrapping, et les affiche dans la console.

3. Créer une base de données avec une table articles_20minutes pour stocker date, catégorie et titre des articles.

4. Modifier le script python pour inscrire les données dans la base


### Ressources
Lien 1 : [Le site 20 minutes][site].  


### Modalité pédagogique :
Travail individuel.

### Livrables :
Un dépot github contenant les scripts python ainsi que l'export SQL de la base créée, et contenant un import des données.

[imageSite]: https://github.com/dev-ia-25/brief_scrapping/blob/main/vue%20site%2020minutes.png?raw=true
[site]: https://www.20minutes.fr/ "Le site 20 Minutes"
