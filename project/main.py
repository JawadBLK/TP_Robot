import sys

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
from robot.capteurs import Lidar,CapteurThermique
from robot.cartographie import Cartographie

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

# ── 2. Ajout des capteurs ──────────────────────────────────────────────
# ... création du Lidar ...
lidar = Lidar(robot, nb_rayons=180, portee_max=6.0)
robot.ajouter_capteur(lidar)

# --- Capteur thermique ---
thermique = CapteurThermique(robot, portee=6.0)
robot.ajouter_capteur(thermique)    

# Interrupteur pour l'affichage thermique
afficher_thermique = False

carto = Cartographie(950, 650)

mode_vue = "NORMAL"  # Modes : "NORMAL", "LIDAR", "CARTO"

# ── 3. Construction du monde ──────────────────────────────────────────────
env.ajouter_robot(robot)

build_plan(env)

# ── 3.1 Ennemis avec des chemins de patrouille ──────────────────────────
ennemi1 = Ennemi(-7, -2, waypoints=[(-7, -2), (-7, -4), (-3, -4), (-3, -4), (-3, -2), (-5, -2), (-5, -4), (-7, -4)])
env.ajouter_ennemi(ennemi1)

ennemi2 = Ennemi(3, -3, waypoints=[(3, -3), (3, -4), (-1, -4), (-1, -3), (3, -3)])
env.ajouter_ennemi(ennemi2)

ennemi3 = Ennemi(-7, 2, waypoints=[(-7, 2), (-7, 4.2), (-3, 4.2), (-3, 2), (-3, 2), (-5, 2), (-5, 3), (-7, 2)])
env.ajouter_ennemi(ennemi3)

ennemi4 = Ennemi(20, 0, waypoints=[(20, 0), (9, 6), (-9, 6), (-9, 0), (7, 0), (-9, 0), (-9, -6), (9, -6), (20, 0)])
env.ajouter_ennemi(ennemi4)

# ── 3.2 Props décoratifs ────────────────────────────────────────────────────
# ── 3.2.1 Salle haut-gauche (x: -8 à -2, y: 1 à 5) ──────────────────────────
env.ajouter_prop(Props(-6, 3.5, "bureau"))         
env.ajouter_prop(Props(-5, 3.5, "chaise"))         
env.ajouter_prop(Props(-3, 4.5, "plante"))         
env.ajouter_prop(Props(-4, 2.5, "ordinateur"))

# ── 3.2.2 Salle haut-milieu (x: -2 à 4, y: 1 à 5) ───────────────────────────
env.ajouter_prop(Props(1,  2.0, "armoire", angle=math.pi/2))  
env.ajouter_prop(Props(-1, 4.0, "bureau"))
env.ajouter_prop(Props(-1, 3.5, "chaise"))
env.ajouter_prop(Props(2,  4.5, "ordinateur"))
env.ajouter_prop(Props(3,  4.5, "lampe"))
env.ajouter_prop(Props(0,  4.6, "plante"))

# ── 3.2.3 Salle haut-droite (x: 4 à 8, y: 1 à 5) ────────────────────────────
env.ajouter_prop(Props(6,  4.0, "bureau"))
env.ajouter_prop(Props(6,  3.5, "chaise"))
env.ajouter_prop(Props(7,  2.5, "armoire"))
env.ajouter_prop(Props(5,  4.8, "plante"))
env.ajouter_prop(Props(7,  4.5, "caisse"))

# ── 3.2.4 Salle bas-gauche (x: -8 à -2, y: -5 à -1) ─────────────────────────
env.ajouter_prop(Props(-3, -1.5, "bureau"))
env.ajouter_prop(Props(-7, -4.5, "caisse"))
env.ajouter_prop(Props(-6, -4.5, "caisse"))
env.ajouter_prop(Props(-3, -4.5, "armoire", angle=math.pi/2))

# ── 3.2.5 Salle bas-milieu (x: -2 à 4, y: -5 à -1) ──────────────────────────
env.ajouter_prop(Props(-1,  -1.45, "bureau"))
env.ajouter_prop(Props(-1,  -1.35, "ordinateur"))
env.ajouter_prop(Props(-1, -4.5, "caisse"))
env.ajouter_prop(Props(0,  -4.5, "caisse"))
env.ajouter_prop(Props(3,  -4.5, "plante"))

# ── 3.2.6 Salle bas-droite (x: 4 à 8, y: -5 à -1) ───────────────────────────
env.ajouter_prop(Props(6,  -2.5, "bureau"))
env.ajouter_prop(Props(6,  -3.0, "chaise"))
env.ajouter_prop(Props(7,  -4.5, "armoire"))
env.ajouter_prop(Props(5,  -4.5, "lampe"))
env.ajouter_prop(Props(7,  -2.5, "tableau"))

print("Nombre d'obstacles :", len(env.obstacles))
print(hasattr(env, "alerte"))

fps = 80
clock = pygame.time.Clock()
#dt = 4.0 / fps
running = True
temps_ecoule = 0.0  # en secondes

# ── Boucle de jeu ──────────────────────────────────────────────
while running:
    dt = clock.tick(fps) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # --- CHANGEMENT DE VUE ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                mode_vue = "NORMAL"
            elif event.key == pygame.K_2:
                mode_vue = "LIDAR"
            elif event.key == pygame.K_3:
                mode_vue = "CARTO"
            elif event.key == pygame.K_t: 
                afficher_thermique = not afficher_thermique
        # -------------------------------

    #--- Récupérer les commandes --- 
    commande = controleur.lire_commande()
    env.robot.commander(**commande)

    # --- Mettre à jour la physique et gérer les collisions ---
    env.mettre_a_jour(dt)
    temps_ecoule += dt

    # --- AJOUT MISE À JOUR CAPTEURS ---
    lidar.read(env)
    thermique.read(env)
    carto.mettre_a_jour(vue, lidar)

    # --- AJOUT AFFICHAGE MODULABLE ---
    if mode_vue == "CARTO":
        # Mode 3 : Vue cartographique avec rayons du Lidar, carte thermique et console
        carto.dessiner(vue.screen)
        if afficher_thermique:
            thermique.draw(vue)
        vue.dessiner_robot(env.robot)
        vue.dessiner_console(env, temps_ecoule)
    else:
        # Modes 1 et 2 : Plan d'architecte classique
        vue.dessiner_environnement(env, temps_ecoule)
        
        # Dessine les obstacles par-dessus le plan d'architecte
        for obs in env.obstacles:
            obs.dessiner(vue)
            
        # Si on est en Mode 2, on superpose les rayons du Lidar
        if mode_vue == "LIDAR":
            lidar.draw(vue)
        if afficher_thermique:
            thermique.draw(vue)

    #image à l'écran
    pygame.display.flip()

pygame.quit()