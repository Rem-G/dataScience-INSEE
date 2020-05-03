
# Projet DataScience

Ce projet a pour but la création d'un dataset offrant différents indicateurs communaux.
L'ensemble des communes de France métropolitaine et d'Outre-mer sont disponibles.

Les indicateurs suivants sont disponibles :

 - Evolution de la population de 1968 à 2016
 - Répartition de la population d'une commune par tranches d'âge
 - Evolution des catégories socio-professionnelles de 1968 à 2016
 - Répartition des catégories socio-professionnelles au sein d'une commune
 - Valeur foncière moyenne du m2 de logement d'une commune
 - Comparaison de la valeur foncière du m2 de logement d'une commune avec le reste du département
 - Commerces disponibles au sein d'une commune
 - Densité de population
 - Taux de chômage

Selon le mode d'étude utilisé, il est possible de sélectionner plusieurs communes et d'en cumuler les indicateurs.

**Le projet est accessible en ligne à l'adresse suivante : [https://insee-dashboard.herokuapp.com/](https://insee-dashboard.herokuapp.com/)**

## Installation  et utilisation :
Au lancement du programme une vérification de la présence des bases de données ainsi que des cartes est effectuée. Si l'un des éléments est manquant il sera recréé automatiquement cependant cette opération peut prendre un certain temps.
### Réinitialisation des données :

|                |                                                  |
|----------------|-------------------------------|
|Bases de données|`src/main.py --dbreset` |
|Cartes          |`src/main.py --mapsreset` 

 ### Lancement version console :
 
 - Executer `src/main.py`

### Lancement version dashboard :

 - Executer `src/dashboard.py`

## Contributeurs :

 - [Thomas-CENCI](http://github.com/Thomas-CENCI/)
 - [Rem-G](http://github.com/Rem-G)

## Trello :
https://trello.com/b/c6u1DuCh/insee

## Sources : 

 - insee.fr
 - data.gouv.fr
 - [https://geo.api.gouv.fr/decoupage-administratif](https://geo.api.gouv.fr/decoupage-administratif)
 - [https://cadastre.data.gouv.fr/data/etalab-dvf/](https://cadastre.data.gouv.fr/data/etalab-dvf/)
