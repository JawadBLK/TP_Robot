# 🤖🪖 Jeu de Détection d'ennemis militaires 🤖🪖
-----------------------------------------------------------------------------------------------------------------------------------------------
##  Description du projet
Ce projet est un simulateur 2D interactif de robot mobile développé en Python. Il a été réalisé dans le cadre du cours de **Programmation Orientée Objet (POO) à destination de la robotique** (Master Data et IA -  Université Catholique de Lille, Année 2025-2026). 

Ce simulateur a pour objectif de détecter des ennemis.
Le robot doit aller à la recherche des ennemis, il connait le nombre d'ennemis dès le début. Les ennemis sont identifiables selon un gradient de couleur visible grâce à un capteur thermique.

----------------------------------------------------------  FONCTIONNALITES -----------------------------------------------------------------------

Le simulateur intègre les fonctionnalités suivantes :
* Moteur Physique & Cinématique : Simulation des déplacements d'un robot (moteur différentiel ou omnidirectionnel) calculés de manière indépendante.
* Environnement Interactif : Le robot évolue dans un plan complet type "Local avec plusieurs pièces" généré dynamiquement, avec la gestion des matériaux (béton, plâtre, portes en bois ouvertes ou fermées).
* Ennemis autonomes : des ennemis sont représentés par des hexagones verts et également un angle de vision de 90°. Les ennemis se déplacent selon des coordonnées de points dans une pièce mais également de l'extérieur du local. Un ennemi possède une température.
* Gestion des Collisions : Le moteur physique empêche le robot de traverser les murs, les portes fermées et les humains, tout en lui permettant de franchir les portes ouvertes.
* Rendu Graphique : Visualisation en temps réel via la bibliothèque `pygame`, avec un suivi du robot (représenté par un visuel personnalisé de R2D2).
* Contrôle Utilisateur : Pilotage fluide du robot au clavier grâce à un contrôleur dédié.

  
-----------------------------------------------------------------------------------------------------------------------------------------------
##  Membres du Groupe
* Marie Willeman
* Quentin Rajski
* Jawad Belkaid

----------------------------------------------------------  LANCEMENT DU SIMULATEUR ---------------------------------------------------------------

## Dépendances nécessaires
Pour faire tourner ce projet, vous aurez besoin de Python 3.x et de la bibliothèque Pygame.
Vous pouvez l'installer via la commande :
`pip install pygame`

## Instructions pour lancer la simulation
1. Clonez ce dépôt GitHub sur votre machine locale.
2. Assurez-vous d'avoir installé les dépendances requises.
3. Ouvrez un terminal à la racine du projet.
4. Exécutez le script principal avec la commande :
`python main.py`
5. Utilisez les flèches directionnelles de votre clavier pour piloter le robot dans l'appartement !
