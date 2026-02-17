from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel, MoteurOmnidirectionnel
from robot.vue import VueTerminal, VuePygame
from robot.controleur import ControleurTerminal
import math
import pygame

# moteur_diff = MoteurDifferentiel()
# moteur_omni = MoteurOmnidirectionnel()
# robot = RobotMobile(0, 0, math.pi/2, moteur_diff)
# robot.afficher()
# robot.avancer(1)
# robot.afficher()
# robot.tourner(math.pi/4)
# robot.afficher()
# robot.x = 10
# robot.afficher()


# dt = 1.0 # pas de temps (s)
# # On doit nommer les arguments (v = ..., omega = ...) car on utilise **kwargs !
# robot.commander(v = 1.0, omega = 0.0) # avance
# robot.mettre_a_jour(dt)
# robot.afficher()
# print(f"Nombre de robots avant : {RobotMobile.nombre_robots()}")

# print("Test du moteur omnidirectionnel :")
# r2 = RobotMobile(0, 0, math.pi/2, moteur_omni)
# r2.commander(vx = 1.0, vy = 0.0, omega = 0.0) # avance
# r2.mettre_a_jour(dt)
# r2.afficher()
# print(f"Nombre de robots après : {RobotMobile.nombre_robots()}")
# print((robot))

# vue = VueTerminal()

# # Utilisation de la vue pour afficher le robot
# vue.dessiner_robot(robot)

moteur_diff = MoteurDifferentiel()
robot = RobotMobile(x=400, y=300, orientation=0, moteur=moteur_diff)
    
# 2. Initialisation du Contrôleur et de la Vue
# La vue Pygame doit ouvrir la fenêtre ici
vue = VuePygame() 
controleur = ControleurTerminal()

dt = 0.1 # Pas de temps
running = True

# 3. Boucle principale (Main Loop)
while running:
    # A. Gestion des événements (indispensable pour Pygame)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # B. Lecture de la commande via le contrôleur
    cmd = controleur.lire_commande()
    
    if cmd is not None:
        # C. Mise à jour du Modèle
        robot.commander(**cmd)
        robot.mettre_a_jour(dt)
        
        # D. Mise à jour de la Vue
        # On limite à 60 FPS comme sur ton image
        vue.tick(60) 
        vue.dessiner_robot(robot)