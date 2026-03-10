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
    def __init__(self, largeur=800, hauteur=600, env_largeur=30, env_hauteur=40):
        pygame.init()
        self.screen = pygame.display.set_mode((largeur, hauteur))
        pygame.display.set_caption("Simulation Robot Mobile")

        self.largeur = largeur
        self.hauteur = hauteur

        self.scale = min(
            largeur / env_largeur,
            hauteur / env_hauteur
        )

        self.clock = pygame.time.Clock()

        # --- Chargement de l'image du robot et du sol  ---
        try:
            # 1. On récupère le dossier où se trouve vue.py (project/robot/)
            dossier_vue = os.path.dirname(os.path.abspath(__file__))
            # 2. On remonte d'un cran pour aller dans le dossier project/
            dossier_project = os.path.dirname(dossier_vue)
            # 3. récupère le chemin complet de l'image à partir du dossier project/
            chemin_image = os.path.join(dossier_project, "image_robot.png")
            
            self.image_robot_originale = pygame.image.load(chemin_image).convert_alpha()
            print("Image de robot chargée avec succès !")
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
        py = int(self.hauteur / 2 - y * self.scale)
        return px, py
    
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

    def dessiner_environnement(self, env):
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

        # 2. FOND INTÉRIEUR (Appartement Beige)
        # On convertit les coordonnées des coins de l'appartement (-8, 5) en haut à gauche et (8, -5) en bas à droite
        px_min, py_max = self.convertir_coordonnees(-8, 5)
        px_max, py_min = self.convertir_coordonnees(8, -5)
        
        largeur_appart = px_max - px_min
        hauteur_appart = py_min - py_max

        rect_appart = pygame.Rect(px_min, py_max, largeur_appart, hauteur_appart)
        pygame.draw.rect(self.screen, (245, 240, 220), rect_appart)


        # 3. Obstacles
        for obs in env.obstacles:
            obs.dessiner(self)

        # 4. Robot
        if env.robot:
            self.dessiner_robot(env.robot)

        pygame.display.flip()

    def dessiner_porte(self, x, y, angle_rad=0, largeur=1.5):
        # 1. On récupère le point d'attache de la porte en pixels
        px, py = self.convertir_coordonnees(x, y)
        
        # 2. On calcule la longueur de la porte en pixels sur l'écran
        longueur_px = int(largeur * self.scale)
        epaisseur_px = max(2, int(0.1 * self.scale)) # Épaisseur visuelle du battant
        
        # 3. On calcule où se termine la porte
        '''Attention : l'axe Y de Pygame est inversé vers le bas, d'où le "py -"''' 
        fin_x = px + longueur_px * math.cos(angle_rad)
        fin_y = py - longueur_px * math.sin(angle_rad)
        
        # 4. On dessine la porte ouverte (marron clair)
        pygame.draw.line(self.screen, (160, 82, 45), (px, py), (fin_x, fin_y), epaisseur_px)