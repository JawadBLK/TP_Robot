import math
import pygame
import os

class VueTerminal:
    def dessiner_robot(self, robot):
        """
        Affiche les informations du robot de manière lisible dans le terminal.
        """
        print("\n=== État du Robot ===")
        print(f"Position    : x = {robot.x:.2f}, y = {robot.y:.2f}")
        print(f"Orientation : {robot.orientation:.2f} rad")
        
        if robot.moteur:
            print(f"Moteur      : {type(robot.moteur).__name__}")
        else:
            print("Moteur      : Aucun")
        print("=====================\n")


class VuePygame:
    CONSOLE_HAUTEUR = 72  # hauteur de la bande console en pixels

    def __init__(self, largeur=800, hauteur=600, env_largeur=30, env_hauteur=40):
        pygame.init()
        self.screen = pygame.display.set_mode((largeur, hauteur))
        pygame.display.set_caption("Simulation Robot Mobile")

        self.largeur = largeur
        self.hauteur = hauteur

        # La zone de jeu est réduite pour laisser la place à la console en bas
        self.hauteur_jeu = hauteur - self.CONSOLE_HAUTEUR

        self.scale = min(
            largeur / env_largeur,
            self.hauteur_jeu / env_hauteur
        )

        self.font       = pygame.font.SysFont("Arial", 32)
        self.font_hud   = pygame.font.SysFont("Courier New", 18, bold=True)
        self.font_label = pygame.font.SysFont("Courier New", 12)
        self.clock = pygame.time.Clock()

        # --- Chargement de l'image du robot ---
        try:
            # 1. On récupère le dossier où se trouve vue.py (project/robot/)
            dossier_vue = os.path.dirname(os.path.abspath(__file__))
            # 2. On remonte d'un cran pour aller dans le dossier project/
            dossier_project = os.path.dirname(dossier_vue)
            # 3. récupère le chemin complet de l'image à partir du dossier project/
            chemin_image = os.path.join(dossier_project, "image_robot.png")
            
            self.image_robot_originale = pygame.image.load(chemin_image).convert_alpha()
            print("Image chargée avec succès !")
        except FileNotFoundError:
            print("Attention: L'image image_robot.png n'a pas été trouvée. Affichage du cercle par défaut.")
            self.image_robot_originale = None

        # --- Chargement de l'image du robot et du sol  ---   
        try:
            chemin_sol = os.path.join(dossier_project, "sol.png")
            self.texture_sol = pygame.image.load(chemin_sol).convert()
            print("Image du sol chargée avec succès !")
        except FileNotFoundError:
            print("Attention: L'image sol.png n'a pas été trouvée. Fond uni utilisé.")
            self.texture_sol = None 

    def convertir_coordonnees(self, x, y):
        px = int(self.largeur / 2 + x * self.scale)
        py = int(self.hauteur_jeu / 2 - y * self.scale)
        return px, py
    


# ──────────────────────────────────────── AFFICHAGE ROBOT  ────────────────────────────────────────
    def dessiner_robot(self, robot):
        if robot is None:
            return

        px, py = self.convertir_coordonnees(robot.x, robot.y)
        r = int(robot.rayon * self.scale)

        # Si l'image a bien été chargée, on l'affiche
        if self.image_robot_originale:
            # 1. On calcule le diamètre en pixels pour la taille de l'image
            diametre = r * 2
            
            # 2. On redimensionne l'image d'origine à la taille physique du robot
            image_redimensionnee = pygame.transform.smoothscale(self.image_robot_originale, (diametre, diametre))
            
            # 3. On fait pivoter l'image selon l'orientation du robot. 
            '''Attention : Pygame tourne dans le sens inverse des aiguilles d'une montre, d'où le signe négatif.'''
            angle_degres = math.degrees(robot.orientation)
            image_tournee = pygame.transform.rotate(image_redimensionnee, angle_degres)
            
            # 4. La rotation modifie la taille de la boîte (rectangle) de l'image. 
            rect = image_tournee.get_rect(center=(px, py))
            
            # Dessine un fin cercle vert pour voir la hitbox de collision physique
            pygame.draw.circle(self.screen, (0, 255, 0), (px, py), r, 1)

            # 5. On "colle" l'image sur l'écran
            self.screen.blit(image_tournee, rect)

            # Ligne rouge orientation du robot
            x_dir = px + int(r * math.cos(robot.orientation))
            y_dir = py - int(r * math.sin(robot.orientation))
            pygame.draw.line(self.screen, (255, 0, 0), (px, py), (x_dir, y_dir), 2)

        # Sinon, l'affichage classique du robot (cercle bleu)
        else:
            pygame.draw.circle(self.screen, (0, 255, 0), (px, py), r, 2)
            pygame.draw.circle(self.screen, (0, 0, 255), (px, py), r - 2)
            x_dir = px + int(r * math.cos(robot.orientation))
            y_dir = py - int(r * math.sin(robot.orientation))
            pygame.draw.line(self.screen, (255, 0, 0), (px, py), (x_dir, y_dir), 2)

    def tick(self, fps=60):
        self.clock.tick(fps)



 # ──────────────────────────────────────── CONSOLE SUIVI JEU  ────────────────────────────────────────
    def _draw_card(self, x, y, w, h, couleur_bord=(50, 80, 120), couleur_fond=(22, 28, 42)):
        """Dessine une carte avec fond sombre et bordure colorée arrondie."""
        pygame.draw.rect(self.screen, couleur_fond, (x, y, w, h), border_radius=6)
        pygame.draw.rect(self.screen, couleur_bord, (x, y, w, h), 1, border_radius=6)

    def dessiner_console(self, env, temps_ecoule):
        """Dessine la bande console en bas de l'écran."""
        y0 = self.hauteur_jeu
        W  = self.largeur
        H  = self.CONSOLE_HAUTEUR

        # ── Fond dégradé simulé (deux rectangles) ──────────────────────────────
        pygame.draw.rect(self.screen, (14, 18, 30), (0, y0,      W, H // 2))
        pygame.draw.rect(self.screen, (10, 13, 22), (0, y0 + H // 2, W, H - H // 2))

        # Ligne de séparation haute avec dégradé visuel (trait + lueur)
        pygame.draw.line(self.screen, (30, 60, 110), (0, y0), (W, y0), 3)
        pygame.draw.line(self.screen, (60, 140, 255), (0, y0), (W, y0), 1)

        # Ligne de séparation basse (très subtile)
        pygame.draw.line(self.screen, (25, 35, 55), (0, y0 + H - 1), (W, y0 + H - 1), 1)

        ticks = pygame.time.get_ticks()

        # ── SECTION GAUCHE : Chronomètre ───────────────────────────────────────
        minutes = int(temps_ecoule) // 60
        secondes = int(temps_ecoule) % 60
        centis = int((temps_ecoule - int(temps_ecoule)) * 100)
        texte_temps = f"{minutes:02d}:{secondes:02d}.{centis:02d}"

        self._draw_card(10, y0 + 6, 155, H - 14, couleur_bord=(40, 80, 140))

        # Petit point d'accent bleu
        pygame.draw.circle(self.screen, (80, 160, 255), (22, y0 + 18), 4)

        label_temps = self.font_label.render("TEMPS ÉCOULÉ", True, (70, 110, 170))
        valeur_temps = self.font_hud.render(texte_temps, True, (180, 215, 255))
        self.screen.blit(label_temps, (32, y0 + 11))
        self.screen.blit(valeur_temps, (18, y0 + 26))

        # ── SECTION CENTRE-GAUCHE : Compteur ennemis + jauge ──────────────────
        nb_total   = len(env.ennemis)
        nb_alertes = sum(1 for e in env.ennemis if e.detecte)
        ratio      = (nb_alertes / nb_total) if nb_total > 0 else 0

        couleur_compteur = (255, 80, 80) if nb_alertes > 0 else (80, 210, 110)
        bord_card_enn    = (120, 30, 30) if nb_alertes > 0 else (30, 90, 50)
        self._draw_card(175, y0 + 6, 170, H - 14, couleur_bord=bord_card_enn)

        pygame.draw.circle(self.screen, couleur_compteur, (187, y0 + 18), 4)
        label_enn = self.font_label.render("ENNEMIS EN ALERTE", True, (70, 110, 170))
        valeur_enn = self.font_hud.render(f"{nb_alertes} / {nb_total}", True, couleur_compteur)
        self.screen.blit(label_enn, (197, y0 + 11))
        self.screen.blit(valeur_enn, (183, y0 + 26))

        # Mini jauge de menace
        jauge_x, jauge_y = 183, y0 + H - 18
        jauge_w = 154
        pygame.draw.rect(self.screen, (30, 35, 50), (jauge_x, jauge_y, jauge_w, 6), border_radius=3)
        if nb_total > 0:
            fill_w = int(jauge_w * ratio)
            col_jauge = (200 + int(55 * ratio), int(180 * (1 - ratio)), 50)
            if fill_w > 0:
                pygame.draw.rect(self.screen, col_jauge, (jauge_x, jauge_y, fill_w, 6), border_radius=3)

        # ── SECTION CENTRE : Statut principal ─────────────────────────────────
        cx = (345 + W - 90) // 2  # centré entre la fin de la carte ennemis et le début FPS
        if env.alerte:
            statut_txt = "! DÉTECTION !"
            statut_col = (255, 70, 70)
            pulse = int(abs(ticks % 700 - 350) / 350 * 100)
            bord_statut = (pulse + 120, 20, 20)
            fond_statut = (pulse // 2 + 40, 8, 8)
        else:
            statut_txt = "SÉCURISÉ"
            statut_col = (60, 220, 100)
            bord_statut = (30, 100, 50)
            fond_statut = (12, 38, 20)

        sw = 200
        self._draw_card(cx - sw // 2, y0 + 6, sw, H - 14,
                        couleur_bord=bord_statut, couleur_fond=fond_statut)

        valeur_statut = self.font_hud.render(statut_txt, True, statut_col)
        rect_s = valeur_statut.get_rect(center=(cx, y0 + H // 2))
        self.screen.blit(valeur_statut, rect_s)

        # ── SECTION DROITE : FPS ───────────────────────────────────────────────
        fps_val = int(self.clock.get_fps())
        fps_col = (80, 200, 80) if fps_val >= 50 else (220, 160, 40) if fps_val >= 30 else (220, 60, 60)
        self._draw_card(W - 90, y0 + 6, 80, H - 14, couleur_bord=(40, 60, 90))

        label_fps = self.font_label.render("FPS", True, (60, 90, 130))
        valeur_fps = self.font_hud.render(str(fps_val), True, fps_col)
        rect_fps_label = label_fps.get_rect(centerx=W - 50, top=y0 + 11)
        rect_fps_val   = valeur_fps.get_rect(centerx=W - 50, top=y0 + 26)
        self.screen.blit(label_fps,  rect_fps_label)
        self.screen.blit(valeur_fps, rect_fps_val)



 # ──────────────────────────────────────── ENVIRONNEMENT : affichage sol, console ────────────────────────────────────────
    def dessiner_environnement(self, env, temps_ecoule=0.0):
         # 1. FOND EXTÉRIEUR (sol)
        if self.texture_sol:
            # On répète la texture de sol comme un calque sur tout l'écran
            l_texture = self.texture_sol.get_width()
            h_texture = self.texture_sol.get_height()
            for x in range(0, self.largeur, l_texture):
                for y in range(0, self.hauteur, h_texture):
                    self.screen.blit(self.texture_sol, (x, y))
        else:
            #  Si l'image sol.png n'est pas là, on met un fond vert uni
            self.screen.fill((120,80,50))

        # 2. FOND INTÉRIEUR (Fond Beige)
        # On convertit les coordonnées des coins de l'appartement (-8, 5) en haut à gauche et (8, -5) en bas à droite
        px_min, py_max = self.convertir_coordonnees(-8, 5)
        px_max, py_min = self.convertir_coordonnees(8, -5)
        
        largeur_appart = px_max - px_min
        hauteur_appart = py_min - py_max

        rect_appart = pygame.Rect(px_min, py_max, largeur_appart, hauteur_appart)
        pygame.draw.rect(self.screen, (245, 240, 220), rect_appart)

        # 3. Dessiner les obstacles
        for obs in env.obstacles:
            obs.dessiner(self)

        # 4. Dessiner les props décoratifs
        for prop in env.props:
            prop.dessiner(self)

        # 5. Dessiner le robot
        if env.robot:
            self.dessiner_robot(env.robot)

        # 6. Dessiner les ennemis
        for ennemi in env.ennemis:
            ennemi.dessiner(self)

        # 7. Alerte en haut de la zone de jeu
        if env.alerte:
            texte = self.font.render(env.alerte, True, (200, 0, 0))
            rect = texte.get_rect(center=(self.largeur // 2, 40))
            self.screen.blit(texte, rect)

        # 8. Console en bas
        self.dessiner_console(env, temps_ecoule)

        pygame.display.flip()


 # ──────────────────────────────────────── PORTE ────────────────────────────────────────

    def dessiner_porte(self, x, y, angle_rad=0, largeur=1.5):
        # 1. On récupère le point d'attache de la porte en pixels
        px, py = self.convertir_coordonnees(x, y)
        
        # 2. On calcule la longueur de la porte en pixels sur l'écran
        longueur_px = int(largeur * self.scale)
        epaisseur_px = max(2, int(0.1 * self.scale)) # Épaisseur visuelle du battant
        
        # 3. On calcule où se termine la porte (trigonométrie classique)
        # Attention : l'axe Y de Pygame est inversé vers le bas, d'où le "py -"
        fin_x = px + longueur_px * math.cos(angle_rad)
        fin_y = py - longueur_px * math.sin(angle_rad)
        
        # 4. On dessine la porte ouverte (marron clair)
        pygame.draw.line(self.screen, (160, 82, 45), (px, py), (fin_x, fin_y), epaisseur_px)