# TP_Robot
Cours Robotique


# Robot_mobile.py 
Principales fonctionalités du robot
- fonction avancer > distance en mètre
- fonction afficher > retourne la position et l'orientation
- fonction tourner > avec un angle en radian 
- getter/setter de la position

- robot(position x, position y, orientation=angle en radian,moteur=None)


# moteur.py 
Le moteur = actionneur du robot
- fonction commander : stocker les vitesses
- fonction mettre_a_jour : position selon la vitesse et la direction (orientation)

2 types de moteurs 
- différentiel : vitesse linéaire et vitesse angulaire > le robot avance uniquement dans la direction de son orientation et peut tourner simultanément
  >>MoteurDifferentiel (v=vitesse linéaire, omega=vitesse angulaire)
- omnidirectionnel  : vitesse dans la direction avant du robot, vitesse dans le direction latérale, vitesse angulaire > robot se déplacer dans toutes les directions, indépendamment de son orientation
  >>MoteurOmnidirectionnel(vx= vitesse direction avant, vy = vitesse direction latérale, omega =vitesse angulaire)

# polymorphisme par composition 

- le même robot peut être équipé de moteurs différents,
- le comportement du robot change sans modifier sa classe,
- le choix du moteur détermine le type de déplacement

=> le robot appelle les mêmes méthodes, mais le comportement dépend du moteur utilisé.

##
