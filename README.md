Cours Robotique M2 Data IA - Marie-Jawad-Quentin


## Robot_mobile.py 
Principales fonctionalités du robot
- méthode avancer > distance en mètre
- méthode afficher > retourne la position et l'orientation
- méthode tourner > avec un angle en radian 
- getter/setter de la position

  >> robot(position x, position y, orientation=angle en radian,moteur=None)
  
Le robot lui stocke l'état (position, orientation)


Ajout de méthodes : 
- nombre_robots : retour le nombre de robots créés
- moteur_valide : confirme si le type de moteur renseigné pour le moteur est bien une instance de la classe moteur

## Moteur.py 
Le moteur = actionneur du robot
- méthode commander : stocker les vitesses
- méthode mettre_a_jour : position selon la vitesse et la direction (orientation)

Le moteur applique la cinématique et la dynamique. 

**2 types de moteurs**

- **différentiel** : vitesse linéaire et vitesse angulaire > **le robot avance uniquement dans la direction de son orientation et peut tourner simultanément**
  >>MoteurDifferentiel (v=vitesse linéaire, omega=vitesse angulaire)


- **omnidirectionnel**  : vitesse dans la direction avant du robot, vitesse dans le direction latérale, vitesse angulaire > **robot se déplacer dans toutes les directions, indépendamment de son orientation**
  >>MoteurOmnidirectionnel(vx= vitesse direction avant, vy = vitesse direction latérale, omega =vitesse angulaire)

## Polymorphisme par composition : 

Quelques propriétés sur le robot : 
- le même robot peut être équipé de moteurs différents,
- le comportement du robot change sans modifier sa classe,
- le choix du moteur détermine le type de déplacement

## Ajout de contrôleurs : 

Les contrôleurs au niveau du terminal permettent de contrôler le robot en mettant des valeurs comme expliqué dans le prompt du terminal. 


## Ajout d'une vue graphique : Pygame

A l'aide d'une interface graphique pygame dans la classe VuePygame, qui encapsule l'ensemble des fonctionnalités graphiques. 
=> le robot appelle les mêmes méthodes, mais le comportement dépend du moteur utilisé.

### Réglages de l'environnement graphique

**Le robot**

- le robot est représenté par un petit cercle et un segment représentant l'orientation

**Les obstacles**

- les obstacles sont définis par des fonctions dessinerType (type= cercle, rectangle...)

