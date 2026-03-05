import pygame
from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel
from robot.controleur import ControleurClavierPygame
from robot.vue import VuePygame
from robot.Environnement import Environnement
from robot.plan_autocad import build_plan
from robot.ennemis import Ennemi

# 1. Initialisation MVC
robot = RobotMobile(x=-8.5, y=0, orientation=0, moteur=MoteurDifferentiel())
controleur = ControleurClavierPygame()

env = Environnement()

vue = VuePygame(
    largeur=800,
    hauteur=600,    
    env_largeur=env.largeur,
    env_hauteur=env.hauteur
)

# 2. Construction du monde
env.ajouter_robot(robot)
build_plan(env)

env.ajouter_ennemi(Ennemi(-6, -4))
env.ajouter_ennemi(Ennemi(4, 2))
env.ajouter_ennemi(Ennemi(8, -6))

print("Nombre d'obstacles :", len(env.obstacles))
print(hasattr(env, "alerte"))

fps = 40
dt = 1.0 / fps
running = True

# 3. Boucle principale
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # A. Récupérer les commandes
    commande = controleur.lire_commande()
    env.robot.commander(**commande)
    if commande["v"] == 0 and commande["omega"] == 0:
        robot.commander(v=0.0, omega=0.0)
    else:
        robot.commander(**commande)

    # B. Mettre à jour la physique et gérer les collisions
    env.mettre_a_jour(dt)
    
    # C. Afficher le nouvel état
    vue.dessiner_environnement(env)
    vue.tick(fps)

pygame.quit()