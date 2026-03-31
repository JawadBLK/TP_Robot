import sys
import pygame
import math
import random
from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel
from robot.controleur import ControleurClavierPygame
from robot.vue import VuePygame
from robot.Environnement import Environnement
from robot.plan_autocad import build_plan
from robot.ennemis import Ennemi
from robot.props import Props
from robot.capteurs import Lidar, CapteurThermique
from robot.cartographie import Cartographie

# ── 1. CONFIGURATION INITIALE ──────────────────────────────────────────
pygame.init()
LARGEUR, HAUTEUR = 950, 650

robot = RobotMobile(x=-8.5, y=0, orientation=0, moteur=MoteurDifferentiel())
controleur = ControleurClavierPygame()

env = Environnement()

vue = VuePygame(
    largeur=LARGEUR,
    hauteur=HAUTEUR,    
    env_largeur=env.largeur,
    env_hauteur=env.hauteur
)

# ── 2. CAPTEURS ET CARTOGRAPHIE ───────────────────────────────────────
lidar = Lidar(robot, nb_rayons=180, portee_max=6.0)
robot.ajouter_capteur(lidar)

thermique = CapteurThermique(robot, portee=6.0)
robot.ajouter_capteur(thermique)    

carto = Cartographie(LARGEUR, HAUTEUR)

afficher_thermique = False
mode_vue = "NORMAL"

# ── 3. CONSTRUCTION DU MONDE ──────────────────────────────────────────
env.ajouter_robot(robot)
build_plan(env)

ennemi1 = Ennemi(-7, -2, waypoints=[(-7, -2), (-7, -4), (-3, -4), (-3, -4), (-3, -2), (-5, -2), (-5, -4), (-7, -4)])
ennemi2 = Ennemi(3, -3,waypoints=[(3, -3), (3, -4), (-1, -4), (-1, -3), (3, -3)])
ennemi3 = Ennemi(-7, 2,waypoints=[(-7, 2), (-7, 4.2), (-3, 4.2), (-3, 2), (-3, 2), (-5, 2), (-5, 3), (-7, 2)])
ennemi4 = Ennemi(20, 0, waypoints=[(20, 0), (9, 6), (-9, 6), (-9, 0), (7, 0), (-9, 0), (-9, -6), (9, -6), (20, 0)])

for e in [ennemi1, ennemi2, ennemi3, ennemi4]:
    env.ajouter_ennemi(e)


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
# ── 4. BOUCLE DE JEU ──────────────────────────────────────────────────
fps = 60
running = True
temps_ecoule = 0.0

env.etat_partie = "MENU"
type_partie = None  # Permettra de savoir si on est en mode "DEMO" ou "JEU"

while running:
    dt = vue.clock.tick(fps) / 1000.0
    
    # --- GESTION DES ÉVÉNEMENTS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            # Échap quitte le jeu peu importe le menu
            if event.key == pygame.K_ESCAPE:
                running = False
            
            # --- CHOIX DANS LE MENU ---
            elif env.etat_partie == "MENU":
                # Mode DÉMO (Touche 1 ou Pavé numérique 1)
                if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                    env.etat_partie = "EN_COURS"
                    type_partie = "DEMO"
                    mode_vue = "NORMAL" # On force la vue 1
                    
                # Mode JEU (Touche 2 ou Pavé numérique 2)
                elif event.key == pygame.K_2 or event.key == pygame.K_KP2:
                    env.etat_partie = "EN_COURS"
                    type_partie = "JEU"
                    mode_vue = "CARTO"  # On force la vue 3
                
            # --- CONTRÔLES EN COURS DE PARTIE ---
            elif env.etat_partie == "EN_COURS":
                # Les changements de vue ne sont autorisés qu'en mode DEMO
                if type_partie == "DEMO":
                    if event.key == pygame.K_1 or event.key == pygame.K_KP1: mode_vue = "NORMAL"
                    if event.key == pygame.K_2 or event.key == pygame.K_KP2: mode_vue = "LIDAR"
                    if event.key == pygame.K_3 or event.key == pygame.K_KP3: mode_vue = "CARTO"
                
                    # === Basculer en Mode JEU avec réinitialisation ===
                    if event.key == pygame.K_j:
                        type_partie = "JEU"
                        mode_vue = "CARTO"
                        
                        # 1. Remise à zéro du robot
                        robot.x = -8.5
                        robot.y = 0
                        robot.orientation = 0
                        robot.commander(v=0, omega=0) # Arrête le robot net
                        
                        # 2. Nettoyage de la carte (on remet tout en noir)
                        carto.surface.fill((0, 0, 0))
                        
                        # 3. Lancement du message "Début de la partie" (pendant 2 secondes)
                        env.temps_debut_jeu = 2.0
                        
                        # 4. Reset des paramètres de jeu
                        env.temps_detection_robot = 0.0
                        temps_ecoule = 0.0 # Reset le chrono
                # Thermique et Flashbang sont autorisés dans les deux modes
                if event.key == pygame.K_t: afficher_thermique = not afficher_thermique
                if event.key == pygame.K_SPACE: env.lancer_flashbang()

            # --- CONTRÔLES SUR L'ÉCRAN DE FIN ---
            elif env.etat_partie in ["VICTOIRE", "ECHEC"]:
                if event.key in [pygame.K_1, pygame.K_KP1, pygame.K_2, pygame.K_KP2]:
                    # Choix du mode
                    if event.key in [pygame.K_1, pygame.K_KP1]:
                        type_partie = "JEU"
                        mode_vue = "CARTO"
                        env.temps_debut_jeu = 2.0  # Message "Début de la partie"
                    else:
                        type_partie = "DEMO"
                        mode_vue = "NORMAL"
                        env.temps_debut_jeu = 0.0
                    
                    # 1. Réinitialisation des paramètres globaux
                    env.etat_partie = "EN_COURS"
                    temps_ecoule = 0.0
                    env.temps_detection_robot = 0.0
                    if hasattr(env, 'temps_effet_flash'):
                        env.temps_effet_flash = 0.0
                    
                    # 2. Réinitialisation du Robot
                    robot.x = -8.5
                    robot.y = 0
                    robot.orientation = 0
                    robot.commander(v=0, omega=0)
                    carto.surface.fill((0, 0, 0)) # On efface la carte
                    
                    # 3. Réinitialisation des Ennemis
                    for e in env.ennemis:
                        e.temps_stun = 0.0       # On les réveille
                        e.detecte = False        # On annule l'alerte
                        e.historique_chaleur = [] # On efface leurs traces thermiques
                        
                        # On les téléporte à leur tout premier waypoint (point de départ)
                        if hasattr(e, 'waypoints') and len(e.waypoints) > 0:
                            e.x = e.waypoints[0][0]
                            e.y = e.waypoints[0][1]
                            e.waypoint_index = 0

    # --- MISE À JOUR PHYSIQUE ---
    if env.etat_partie == "EN_COURS":
        commande = controleur.lire_commande()
        if commande:
            robot.commander(**commande)
            
        env.mettre_a_jour(dt)
        temps_ecoule += dt
        
        lidar.read(env)
        thermique.read(env)
        carto.mettre_a_jour(vue, lidar)

    # --- DESSIN DU MONDE (Arrière-plan) ---
    if mode_vue == "CARTO":
        carto.dessiner(vue.screen)
        if afficher_thermique: thermique.draw(vue)
        vue.dessiner_robot(robot)
    else:
        vue.dessiner_environnement(env, temps_ecoule)
        for obs in env.obstacles: obs.dessiner(vue)
        for prop in env.props: prop.dessiner(vue)
        for ennemi in env.ennemis: ennemi.dessiner(vue)
        
        if mode_vue == "LIDAR": lidar.draw(vue)
        if afficher_thermique: thermique.draw(vue)

    # --- EFFET FLASHBANG ---
    if hasattr(env, 'temps_effet_flash') and env.temps_effet_flash > 0:
        intensite = 15.0 
        shake_x = int(random.uniform(-1, 1) * intensite * env.temps_effet_flash)
        shake_y = int(random.uniform(-1, 1) * intensite * env.temps_effet_flash)
        bloom = 1.0 + (0.05 * env.temps_effet_flash)
        
        capture = vue.screen.copy()
        vue.screen.fill((0, 0, 0))
        
        p_surf = pygame.transform.scale(capture, (int(LARGEUR * bloom), int(HAUTEUR * bloom)))
        p_rect = p_surf.get_rect(center=(LARGEUR//2 + shake_x, HAUTEUR//2 + shake_y))
        vue.screen.blit(p_surf, p_rect)
        
        alpha = int(255 * min(1.0, env.temps_effet_flash / 0.3))
        white_surf = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
        white_surf.fill((255, 255, 255, alpha))
        vue.screen.blit(white_surf, (0, 0))

    # --- INTERFACE HUD ---
    if env.etat_partie != "MENU":
        vue.dessiner_console(env, temps_ecoule, type_partie=type_partie)

    # ========================================================
    # --- ÉCRAN D'ACCUEIL (MENU) ---
    # ========================================================
    if env.etat_partie == "MENU":
        overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 240)) # Fond très sombre
        vue.screen.blit(overlay, (0, 0))
        
        f_titre = pygame.font.SysFont("Courier New", 38, bold=True)
        f_texte = pygame.font.SysFont("Courier New", 16)
        f_action = pygame.font.SysFont("Courier New", 22, bold=True)
        
        # Titre
        titre = f_titre.render("DÉTECTION D'ENNEMIS MILITAIRE", True, (255, 200, 50))
        vue.screen.blit(titre, titre.get_rect(center=(LARGEUR//2, 100)))
        
        # Règles
        regles = [
            "--- RÈGLES DE LA MISSION ---",
            "Retrouvez les ennemis à l'aide des différentes vues.",
            "Neutralisez tous les ennemis en même temps pour la victoire.",
            "Attention : si vous êtes détecté plus de 1.5s, la mission échoue."
        ]
        for i, ligne in enumerate(regles):
            coul = (200, 220, 255) if i > 0 else (100, 150, 255)
            txt = f_texte.render(ligne, True, coul)
            vue.screen.blit(txt, txt.get_rect(center=(LARGEUR//2, 200 + i * 30)))
            
        # Touches
        touches = [
            "--- CONTRÔLES  ---",
            "[FLÈCHES] : Déplacer le robot",
            "[T] Thermique   [ESPACE] Flashbang   [ECHAP] Quitter",
            "--- CONTRÔLES DEMO VUE ---",
            "[1] Normale   [2] Lidar   [3] Cartographie",
        ]
        for i, ligne in enumerate(touches):
            coul = (150, 255, 150) if i > 0 else (100, 255, 100)
            txt = f_texte.render(ligne, True, coul)
            vue.screen.blit(txt, txt.get_rect(center=(LARGEUR//2, 350 + i * 30)))
            
        # Choix du mode (avec clignotement)
        pulse = abs(math.sin(pygame.time.get_ticks() / 300.0))
        alpha = int(255 * pulse)
        
        txt_demo = f_action.render("Appuyez sur [1] pour le Mode DÉMO (Toutes vues)", True, (150, 200, 255))
        txt_jeu = f_action.render("Appuyez sur [2] pour le Mode JEU (Carto uniquement)", True, (255, 100, 100))
        
        txt_demo.set_alpha(alpha)
        txt_jeu.set_alpha(alpha)
        
        vue.screen.blit(txt_demo, txt_demo.get_rect(center=(LARGEUR//2, 500)))
        vue.screen.blit(txt_jeu, txt_jeu.get_rect(center=(LARGEUR//2, 550)))

    # ========================================================
    # --- ÉCRAN DE FIN (VICTOIRE / ÉCHEC) ---
    # ========================================================
    # ========================================================
    # --- ÉCRAN DE FIN (VICTOIRE / ÉCHEC) ---
    # ========================================================
    elif env.etat_partie != "EN_COURS":
        overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220)) # Fond légèrement plus sombre
        vue.screen.blit(overlay, (0, 0))
        
        f_titre = pygame.font.SysFont("Courier New", 50, bold=True)
        f_info = pygame.font.SysFont("Courier New", 22)
        f_choix = pygame.font.SysFont("Courier New", 20, bold=True)
        
        # 1. Le Titre et le sous-titre
        if env.etat_partie == "VICTOIRE":
            txt = f_titre.render("VICTOIRE !", True, (50, 255, 50))
            sub = f_info.render("Tous les ennemis ont été neutralisés.", True, (200, 255, 200))
        else:
            txt = f_titre.render("ÉCHEC CRITIQUE", True, (255, 50, 50))
            sub = f_info.render("Vous avez été détecté.", True, (255, 200, 200))
            
        # 2. Les nouveaux choix
        choix1 = f_choix.render("[1] Rejouer la Mission (Mode JEU)", True, (255, 200, 50))
        choix2 = f_choix.render("[2] Retourner au Mode DÉMO", True, (150, 200, 255))
        choix3 = f_choix.render("[ECHAP] Quitter", True, (150, 150, 150))
        
        # 3. Affichage bien centré
        vue.screen.blit(txt, txt.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 60)))
        vue.screen.blit(sub, sub.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 10)))
        
        vue.screen.blit(choix1, choix1.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 50)))
        vue.screen.blit(choix2, choix2.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 90)))
        vue.screen.blit(choix3, choix3.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 130)))

    pygame.display.flip()

pygame.quit()
sys.exit()