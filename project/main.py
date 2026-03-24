import pygame
import math
from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel
from robot.controleur import ControleurClavierPygame
from robot.vue import VuePygame
from robot.Environnement import Environnement
from robot.plan_autocad import build_plan
from robot.ennemis import Ennemi
from robot.props import Props

# ── 1. Initialisation MVC ──────────────────────────────────────────────
robot = RobotMobile(x=-8.5, y=0, orientation=0, moteur=MoteurDifferentiel())
controleur = ControleurClavierPygame()

env = Environnement()

vue = VuePygame(
    largeur=900,
    hauteur=650,    
    env_largeur=env.largeur,
    env_hauteur=env.hauteur
)

# ── 2. Construction du monde ──────────────────────────────────────────────
env.ajouter_robot(robot)

build_plan(env)

# ── 2.1 Ennemis avec des chemins de patrouille ──────────────────────────
ennemi1 = Ennemi(-7, -2, waypoints=[(-7, -2), (-7, -4), (-3, -4), (-3, -4), (-3, -2), (-5, -2), (-5, -4), (-7, -4)])
env.ajouter_ennemi(ennemi1)

ennemi2 = Ennemi(3, -3, waypoints=[(3, -3), (3, -4), (-1, -4), (-1, -3), (3, -3)])
env.ajouter_ennemi(ennemi2)

ennemi3 = Ennemi(-7, 2, waypoints=[(-7, 2), (-7, 4.2), (-3, 4.2), (-3, 2), (-3, 2), (-5, 2), (-5, 3), (-7, 2)])
env.ajouter_ennemi(ennemi3)

ennemi4 = Ennemi(20, 0, waypoints=[(20, 0), (9, 6), (-9, 6), (-9, 0), (7, 0), (-9, 0), (-9, -6), (9, -6), (20, 0)])
env.ajouter_ennemi(ennemi4)

# ── 2.2 Props décoratifs ────────────────────────────────────────────────────
# ── 2.2.1 Salle haut-gauche (x: -8 à -2, y: 1 à 5) ──────────────────────────
env.ajouter_prop(Props(-6, 3.5, "bureau"))         
env.ajouter_prop(Props(-5, 3.5, "chaise"))         
env.ajouter_prop(Props(-3, 4.5, "plante"))         
env.ajouter_prop(Props(-4, 2.5, "ordinateur"))

# ── 2.2.2 Salle haut-milieu (x: -2 à 4, y: 1 à 5) ───────────────────────────
env.ajouter_prop(Props(1,  2.0, "armoire", angle=math.pi/2))  
env.ajouter_prop(Props(-1, 4.0, "bureau"))
env.ajouter_prop(Props(-1, 3.5, "chaise"))
env.ajouter_prop(Props(2,  4.5, "ordinateur"))
env.ajouter_prop(Props(3,  4.5, "lampe"))
env.ajouter_prop(Props(0,  4.6, "plante"))

# ── 2.2.3 Salle haut-droite (x: 4 à 8, y: 1 à 5) ────────────────────────────
env.ajouter_prop(Props(6,  4.0, "bureau"))
env.ajouter_prop(Props(6,  3.5, "chaise"))
env.ajouter_prop(Props(7,  2.5, "armoire"))
env.ajouter_prop(Props(5,  4.8, "plante"))
env.ajouter_prop(Props(7,  4.5, "caisse"))

# ── 2.2.4 Salle bas-gauche (x: -8 à -2, y: -5 à -1) ─────────────────────────
env.ajouter_prop(Props(-3, -1.5, "bureau"))
env.ajouter_prop(Props(-7, -4.5, "caisse"))
env.ajouter_prop(Props(-6, -4.5, "caisse"))
env.ajouter_prop(Props(-3, -4.5, "armoire", angle=math.pi/2))

# ── 2.2.5 Salle bas-milieu (x: -2 à 4, y: -5 à -1) ──────────────────────────
env.ajouter_prop(Props(-1,  -1.45, "bureau"))
env.ajouter_prop(Props(-1,  -1.35, "ordinateur"))
env.ajouter_prop(Props(-1, -4.5, "caisse"))
env.ajouter_prop(Props(0,  -4.5, "caisse"))
env.ajouter_prop(Props(3,  -4.5, "plante"))

# ── 2.2.6 Salle bas-droite (x: 4 à 8, y: -5 à -1) ───────────────────────────
env.ajouter_prop(Props(6,  -2.5, "bureau"))
env.ajouter_prop(Props(6,  -3.0, "chaise"))
env.ajouter_prop(Props(7,  -4.5, "armoire"))
env.ajouter_prop(Props(5,  -4.5, "lampe"))
env.ajouter_prop(Props(7,  -2.5, "tableau"))

print("Nombre d'obstacles :", len(env.obstacles))
print(hasattr(env, "alerte"))

fps = 80
dt = 4.0 / fps
running = True
temps_ecoule = 0.0  # en secondes

# 3. Boucle principale
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 3.1 Récupérer les commandes
    commande = controleur.lire_commande()
    env.robot.commander(**commande)
    if commande["v"] == 0 and commande["omega"] == 0:
        robot.commander(v=0.0, omega=0.0)
    else:
        robot.commander(**commande)

    # 3.2 Mettre à jour la physique et gérer les collisions
    env.mettre_a_jour(dt)
    temps_ecoule += dt
    
    # 3.3 Afficher le nouvel état
    vue.dessiner_environnement(env, temps_ecoule)
    vue.tick(fps)

pygame.quit()