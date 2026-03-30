"""
main.py
=======
Point d'entrée de la simulation robot mobile.

Raccourcis clavier
------------------
  Flèches        → déplacer le robot (ControleurClavierPygame)
  L              → afficher / masquer les rayons Lidar
  O              → afficher / masquer la grille d'occupation (cartographie)
  T              → basculer en mode caméra thermique
  Échap / Fermer → quitter

Architecture instanciée
-----------------------
  RobotMobile  +  MoteurDifferentiel
  Environnement  (plan_autocad → murs, portes, props, ennemis)
  Lidar          → 180 rayons, portée 6 m
  CapteurThermique → carte gaussienne accumulée
  GrilleOccupation + Cartographe
  VuePygame      (rendu + console HUD)
"""

import sys, os, pygame

# Tous les modules sont dans le sous-dossier robot/
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'robot'))

# ── Modules projet ───────────────────────────────────────────────────────────
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
from robot.cartographie import Cartographe
from robot.capteurs import Lidar, CapteurThermique
from robot.grille_occup import GrilleOccupation
from robot.flashbang import Flashbang

# ════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════
 
FPS          = 60
WINDOW_W     = 1100
WINDOW_H     = 700
ENV_W        = 20       # mètres
ENV_H        = 12       # mètres
 
# Lidar
LIDAR_NB_RAYONS  = 180
LIDAR_PORTEE     = 6.0
LIDAR_BRUIT      = 0.02
 
# Cartographie
CARTO_RESOLUTION = 0.08    # mètres / cellule — plus fin = murs mieux alignés
 
# Thermique
THERMO_RESOLUTION = 0.15
THERMO_SIGMA      = 0.35   # gaussienne plus serrée → trace collée à l'ennemi
THERMO_DECAY      = 0.90   # refroidissement plus rapide → trace courte
THERMO_INTENSITE  = 1.5
THERMO_BRUIT      = 0.008  # bruit réduit → moins de détection parasite
 
 
# ════════════════════════════════════════════════════════════════════════════
#  PATCH VuePygame : ajout des méthodes dessiner_lidar / dessiner_grille
# ════════════════════════════════════════════════════════════════════════════
 
def _patch_vue(vue_class):
    """
    Ajoute dynamiquement les méthodes de dessin des nouveaux modules à VuePygame
    sans modifier vue.py original.
    """
 
    def dessiner_fond_seulement(self, env):
        """
        Dessine uniquement le fond + obstacles + props.
        Le robot et les ennemis sont omis ici car redessinés APRÈS le brouillard.
        """
        import pygame as _pg
        # Fond extérieur
        if self.texture_sol:
            lw = self.texture_sol.get_width()
            lh = self.texture_sol.get_height()
            for x in range(0, self.largeur, lw):
                for y in range(0, self.hauteur, lh):
                    self.screen.blit(self.texture_sol, (x, y))
        else:
            self.screen.fill((120, 80, 50))
        # Fond intérieur beige
        px_min, py_max = self.convertir_coordonnees(-8,  5)
        px_max, py_min = self.convertir_coordonnees( 8, -5)
        _pg.draw.rect(self.screen, (245, 240, 220),
                      _pg.Rect(px_min, py_max, px_max - px_min, py_min - py_max))
        # Obstacles et props
        for obs in env.obstacles:
            obs.dessiner(self)
        for prop in env.props:
            prop.dessiner(self)
 
    def dessiner_lidar(self, lidar, env):
        lidar.dessiner(self, env)
 
    def dessiner_grille(self, grille):
        grille.dessiner(self)
 
    def dessiner_thermique(self, thermo, env):
        thermo.dessiner(self, env)
 
    def dessiner_legende_mode(self, mode_thermo, mode_lidar, mode_carto):
        """Affiche les indicateurs de mode actif en haut à gauche."""
        font = pygame.font.SysFont("Courier New", 12, bold=True)
        items = [
            (f"[L] LIDAR DEBUG {'ON' if mode_lidar else 'OFF'}",
             (80, 220, 80) if mode_lidar else (80, 80, 80)),
            (f"[O] BROUILLARD {'ON' if mode_carto else 'OFF'}",
             (80, 160, 255) if mode_carto else (80, 80, 80)),
            (f"[T] THERMIQUE {'ON' if mode_thermo else 'OFF'}",
             (255, 140, 40) if mode_thermo else (80, 80, 80)),
        ]
        x0, y0 = 8, 8
        for i, (txt, col) in enumerate(items):
            surf = font.render(txt, True, col)
            self.screen.blit(surf, (x0, y0 + i * 16))
 
    def dessiner_impacts(self, lidar):
        lidar.dessiner_impacts(self)
 
    vue_class.dessiner_fond_seulement = dessiner_fond_seulement
    vue_class.dessiner_lidar          = dessiner_lidar
    vue_class.dessiner_grille         = dessiner_grille
    vue_class.dessiner_thermique      = dessiner_thermique
    vue_class.dessiner_impacts        = dessiner_impacts
    vue_class.dessiner_legende_mode   = dessiner_legende_mode
 
 
_patch_vue(VuePygame)
 
# ── Patch Environnement : bloquer les ennemis aveuglés ───────────────────────
_mettre_a_jour_original = Environnement.mettre_a_jour
 
def _mettre_a_jour_patche(self, dt):
    # Sauvegarder position + stats des ennemis aveuglés AVANT la mise à jour
    sauvegardes = {}
    for ennemi in self.ennemis:
        if getattr(ennemi, "aveugle", False):
            sauvegardes[ennemi] = (ennemi.x, ennemi.y, ennemi.angle)
 
    # Appel normal
    _mettre_a_jour_original(self, dt)
 
    # Restaurer position + angle des ennemis aveuglés (annule tout mouvement)
    for ennemi, (x, y, angle) in sauvegardes.items():
        ennemi.x     = x
        ennemi.y     = y
        ennemi.angle = angle
        ennemi.detecte = False
 
Environnement.mettre_a_jour = _mettre_a_jour_patche
 
 
# ════════════════════════════════════════════════════════════════════════════
#  CONSTRUCTION DE LA SCÈNE
# ════════════════════════════════════════════════════════════════════════════
 
def build_scene():
    env = Environnement(largeur=ENV_W, hauteur=ENV_H)
 
    # Robot
    moteur = MoteurDifferentiel()
    robot  = RobotMobile(x=-6.0, y=0.0, orientation=0.0, moteur=moteur)
    env.ajouter_robot(robot)
 
    # Plan (murs, portes)
    build_plan(env)
 
    # Props décoratifs
    props_data = [
        (-5.5,  3.0, "bureau"),
        (-4.5,  3.0, "chaise"),
        (-5.5, -3.0, "armoire"),
        ( 0.5,  3.5, "plante"),
        ( 0.5, -3.5, "plante"),
        ( 6.0,  3.0, "bureau"),
        ( 6.5,  3.0, "ordinateur"),
        ( 6.0, -3.0, "caisse"),
        ( 6.5, -3.0, "caisse"),
        (-1.5,  3.5, "tableau"),
        (-1.5, -3.5, "tableau"),
    ]
    for x, y, t in props_data:
        env.ajouter_prop(Props(x, y, t))
 
    # Ennemis avec des chemins de patrouille
    ennemi1 = Ennemi(-7, -2, waypoints=[(-7, -2), (-7, -4), (-3, -4), (-3, -4), (-3, -2), (-5, -2), (-5, -4), (-7, -4)])
    env.ajouter_ennemi(ennemi1)
    ennemi2 = Ennemi(3, -3, waypoints=[(3, -3), (3, -4), (-1, -4), (-1, -3), (3, -3)])
    env.ajouter_ennemi(ennemi2)
    ennemi3 = Ennemi(-7, 2, waypoints=[(-7, 2), (-7, 4.2), (-3, 4.2), (-3, 2), (-3, 2), (-5, 2), (-5, 3), (-7, 2)])
    env.ajouter_ennemi(ennemi3)
    ennemi4 = Ennemi(20, 0, waypoints=[(20, 0), (9, 6), (-9, 6), (-9, 0), (7, 0), (-9, 0), (-9, -6), (9, -6), (20, 0)])
    env.ajouter_ennemi(ennemi4)
 
    return env
 
 
# ════════════════════════════════════════════════════════════════════════════
#  BOUCLE PRINCIPALE
# ════════════════════════════════════════════════════════════════════════════
 
def _dessiner_barre_detection(screen, largeur, hauteur, temps_detection, seuil):
    """Barre de danger rouge en haut, se remplit pendant la détection."""
    fraction = min(1.0, temps_detection / seuil)
    bw = int(largeur * fraction)
    bh = 6
    # Couleur : jaune → rouge selon l avancement
    r = 255
    g = int(200 * (1 - fraction))
    pygame.draw.rect(screen, (r, g, 0), (0, 0, bw, bh))
    # Clignotement si danger imminent (> 70%)
    if fraction > 0.7:
        ticks = pygame.time.get_ticks()
        if (ticks // 200) % 2 == 0:
            font = pygame.font.SysFont("Arial", 14, bold=True)
            txt = font.render("⚠ DÉTECTÉ !", True, (255, 80, 80))
            screen.blit(txt, (largeur // 2 - txt.get_width() // 2, 10))
 
 
def _dessiner_echec(screen, largeur, hauteur):
    """Overlay rouge d échec."""
    ticks = pygame.time.get_ticks()
    pulse = int(20 * abs(math.sin(ticks * 0.002)))
    overlay = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
    overlay.fill((180 + pulse, 0, 0, 150))
    screen.blit(overlay, (0, 0))
 
    font_titre  = pygame.font.SysFont("Arial", 64, bold=True)
    font_detail = pygame.font.SysFont("Courier New", 22, bold=True)
 
    titre = font_titre.render("ÉCHEC !", True, (255, 255, 255))
    screen.blit(titre, titre.get_rect(center=(largeur // 2, hauteur // 2 - 50)))
 
    detail = font_detail.render("Le robot a été détecté trop longtemps.", True, (255, 200, 200))
    screen.blit(detail, detail.get_rect(center=(largeur // 2, hauteur // 2 + 20)))
 
    hint = font_detail.render("Appuyez sur ÉCHAP pour quitter", True, (220, 180, 180))
    screen.blit(hint, hint.get_rect(center=(largeur // 2, hauteur // 2 + 60)))
 
 
def _dessiner_reussite(screen, largeur, hauteur, temps_ecoule):
    """Overlay de victoire : fond vert semi-transparent + texte centré."""
    ticks = pygame.time.get_ticks()
 
    # Fond vert semi-transparent qui pulse légèrement
    pulse = int(30 * abs(math.sin(ticks * 0.002)))
    overlay = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
    overlay.fill((0, 180 + pulse, 60, 140))
    screen.blit(overlay, (0, 0))
 
    font_titre  = pygame.font.SysFont("Arial", 64, bold=True)
    font_detail = pygame.font.SysFont("Courier New", 22, bold=True)
 
    # Titre
    titre = font_titre.render("RÉUSSITE !", True, (255, 255, 255))
    screen.blit(titre, titre.get_rect(center=(largeur // 2, hauteur // 2 - 50)))
 
    # Temps
    m = int(temps_ecoule) // 60
    s = int(temps_ecoule) % 60
    detail = font_detail.render(f"Tous les ennemis neutralisés en {m:02d}:{s:02d}", True, (200, 255, 200))
    screen.blit(detail, detail.get_rect(center=(largeur // 2, hauteur // 2 + 20)))
 
    # Instruction
    hint = font_detail.render("Appuyez sur ÉCHAP pour quitter", True, (180, 230, 180))
    screen.blit(hint, hint.get_rect(center=(largeur // 2, hauteur // 2 + 60)))
 
 
def main():
    # ── Instanciation ────────────────────────────────────────────────────────
    env        = build_scene()
    vue        = VuePygame(WINDOW_W, WINDOW_H, env_largeur=ENV_W, env_hauteur=ENV_H)
    controleur = ControleurClavierPygame(v_max=2.5, omega_max=1.5)
 
    # Lidar
    lidar = Lidar(
        nb_rayons=LIDAR_NB_RAYONS,
        max_range=LIDAR_PORTEE,
        bruit_sigma=LIDAR_BRUIT,
    )
 
    # Cartographie
    grille   = GrilleOccupation(ENV_W, ENV_H, CARTO_RESOLUTION)
    carte    = Cartographe(grille)
 
    # Flashbang
    flashbang = Flashbang(rayon=4.0, duree_effet=120.0, recharge=5.0)
 
    # Capteur thermique
    thermo = CapteurThermique(
        largeur_m=ENV_W,
        hauteur_m=ENV_H,
        resolution=THERMO_RESOLUTION,
        sigma=THERMO_SIGMA,
        decay=THERMO_DECAY,
        intensite=THERMO_INTENSITE,
        bruit_amplitude=THERMO_BRUIT,
    )
 
    # ── États des modes ──────────────────────────────────────────────────────
    mode_lidar  = True
    mode_carto  = True
    mode_thermo = False
 
    temps_ecoule   = 0.0
    temps_detection = 0.0   # durée cumulée de détection par un ennemi
    victoire        = False  # une fois True, reste True
    echec           = False  # une fois True, reste True
    temps_final     = 0.0   # temps figé à la victoire
    clock = pygame.time.Clock()
 
    # ── Boucle ───────────────────────────────────────────────────────────────
    running = True
    while running:
 
        dt = clock.tick(FPS) / 1000.0
 
        # Timer figé en cas de victoire ou échec
        if not victoire and not echec:
            temps_ecoule += dt
 
        # ── Événements ───────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_l:
                    mode_lidar = not mode_lidar
                elif event.key == pygame.K_o:
                    mode_carto = not mode_carto
                elif event.key == pygame.K_t:
                    mode_thermo = not mode_thermo
                elif event.key == pygame.K_SPACE:
                    flashbang.lancer(env)
 
        # ── Commande robot ───────────────────────────────────────────────────
        cmd = controleur.lire_commande()
        if cmd:
            env.robot.commander(v=cmd["v"], omega=cmd["omega"])
 
        # ── Mise à jour physique (bloquée si victoire/échec) ────────────────
        if not victoire and not echec:
            flashbang.mettre_a_jour(dt)
            env.mettre_a_jour(dt)
 
            # ── Capteurs ─────────────────────────────────────────────────────
            lidar.lire(env)
            carte.mise_a_jour(env, lidar)
            thermo.lire(env)
 
            # ── Condition ÉCHEC : détecté > 3 secondes cumulées ──────────────
            detecte_maintenant = any(e.detecte for e in env.ennemis)
            if detecte_maintenant:
                temps_detection += dt
                if temps_detection >= 3.0:
                    echec = True
            else:
                temps_detection = max(0.0, temps_detection - dt * 0.5)
 
            # ── Condition VICTOIRE : tous les ennemis neutralisés ─────────────
            if (len(env.ennemis) > 0
                    and all(getattr(e, "aveugle", False) for e in env.ennemis)):
                if not victoire:
                    victoire    = True
                    temps_final = temps_ecoule
 
        # ── Rendu ────────────────────────────────────────────────────────────
 
        # 1. Fond complet (murs, props — révélés progressivement via le fog)
        vue.dessiner_fond_seulement(env)
 
        # 2. Brouillard : noir total sauf trous transparents là où le Lidar est passé
        #    O permet de désactiver le brouillard pour voir la map complète
        if mode_carto:
            vue.dessiner_grille(grille)
 
        # 3. Thermique PAR-DESSUS le brouillard :
        #    les signatures thermiques des ennemis sont visibles même dans le noir
        if mode_thermo:
            vue.dessiner_thermique(thermo, env)
 
        # 4. Points d impact Lidar (murs détectés en orange, par-dessus le fog)
        vue.dessiner_impacts(lidar)
 
        # 5. Robot (toujours visible — point de vue du joueur)
        if env.robot:
            vue.dessiner_robot(env.robot)
 
        # Alerte détection
        if env.alerte:
            texte = vue.font.render(env.alerte, True, (200, 0, 0))
            vue.screen.blit(texte, texte.get_rect(center=(vue.largeur // 2, 40)))
 
        # 6. Rayons Lidar (debug, toggle L)
        if mode_lidar:
            vue.dessiner_lidar(lidar, env)
 
        # 7. Flashbang : ennemis neutralisés (rouge clignotant) + flash + onde + HUD
        flashbang.dessiner_ennemis_neutralises(vue, env)
        flashbang.dessiner(vue)
 
        # 8. HUD
        vue.dessiner_console(env, temps_ecoule)
        vue.dessiner_legende_mode(mode_thermo, mode_lidar, mode_carto)
 
        # 9. Barre de détection (danger progressif)
        if temps_detection > 0 and not echec and not victoire:
            _dessiner_barre_detection(vue.screen, vue.largeur, vue.hauteur_jeu,
                                      temps_detection, seuil=3.0)
 
        # 10. Écrans de fin
        if victoire:
            _dessiner_reussite(vue.screen, vue.largeur, vue.hauteur_jeu, temps_final)
        elif echec:
            _dessiner_echec(vue.screen, vue.largeur, vue.hauteur_jeu)
 
        pygame.display.flip()
 
    pygame.quit()
    sys.exit()
 
 
if __name__ == "__main__":
    main()