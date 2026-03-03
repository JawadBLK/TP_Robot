from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel, MoteurOmnidirectionnel
from robot.vue import VueTerminal, VuePygame
from robot.controleur import ControleurTerminal
from robot.controleur import ControleurClavierPygame
from robot.obstacle import ObstacleCirculaire, ObstacleRectangulaire
from robot.Environnement import Environnement
from robot.plan_autocad import build_plan
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
# moteur_diff = MoteurDifferentiel()
# # On initialise au centre de l'écran (0,0 dans le modèle)
# robot = RobotMobile(x=0, y=0, orientation=0, moteur=moteur_diff)

# vue = VuePygame() 
# controleur = ControleurClavierPygame() # <--- On instancie le nouveau

# dt = 0.05 # Pas de temps plus petit pour plus de fluidité
# running = True

# while running:
#     # A. Événements (pour quitter proprement)
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     # B. Lecture instantanée des touches (non-bloquant)
#     cmd = controleur.lire_commande()
    
#     # C. Mise à jour du Modèle
#     robot.commander(**cmd)
#     robot.mettre_a_jour(dt)
        
#     # D. Mise à jour de la Vue
#     vue.tick(60) 
#     vue.dessiner_robot(robot)

print("\n=== Lancement de l'environnement ===")

robot = RobotMobile(x=0, y=-15, orientation=0, moteur=MoteurDifferentiel())
robot.afficher()
robot.commander(v=3.0, omega=0.5)
robot.mettre_a_jour(3.0)
robot.afficher()

env = Environnement()
obs = ObstacleCirculaire(x=2, y=2, rayon=1)
env.ajouter_obstacle(obs)
env.ajouter_robot(robot)

build_plan(env)
print("Nombre d'obstacles :", len(env.obstacles))

vue = VuePygame(
    largeur=800,
    hauteur=600,    
    env_largeur=env.largeur,
    env_hauteur=env.hauteur
)

controleur = ControleurClavierPygame()

dt = 0.05
running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    commande = controleur.lire_commande()  

    if commande["v"] == 0 and commande["omega"] == 0:
        robot.commander(v=2.0, omega=0.0)
    else:
        robot.commander(**commande)

    env.mettre_a_jour(dt)
    
    vue.dessiner_environnement(env)

    pygame.display.flip()

    vue.tick(20)

pygame.quit()