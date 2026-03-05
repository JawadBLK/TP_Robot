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

        # --- Chargement de l'image du robot ---
        try:
            # 1. On récupère le dossier où se trouve vue.py (project/robot/)
            dossier_vue = os.path.dirname(os.path.abspath(__file__))
            # 2. On remonte d'un cran pour aller dans le dossier project/
            dossier_project = os.path.dirname(dossier_vue)
            # 3. On colle le nom de l'image pour avoir le chemin parfait !
            chemin_image = os.path.join(dossier_project, "image_robot.png")
            
            self.image_robot_originale = pygame.image.load(chemin_image).convert_alpha()
            print("Image chargée avec succès !")
        except FileNotFoundError:
            print("Attention: L'image image_robot.png n'a pas été trouvée. Affichage du cercle par défaut.")
            self.image_robot_originale = None



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
            # Pygame tourne en degrés, on convertit donc les radians du modèle.
            angle_degres = math.degrees(robot.orientation)
            image_tournee = pygame.transform.rotate(image_redimensionnee, angle_degres)
            
            # 4. La rotation modifie la taille de la boîte (rectangle) de l'image. 
            # On doit récupérer le nouveau rectangle et le re-centrer sur (px, py)
            rect = image_tournee.get_rect(center=(px, py))
            
            # Dessin un fin cercle vert pour voir la hitbox de collision physique
            pygame.draw.circle(self.screen, (0, 255, 0), (px, py), r, 1)

            # 5. On "colle" l'image sur l'écran
            self.screen.blit(image_tournee, rect)
            # Orientation
            x_dir = px + int(r * math.cos(robot.orientation))
            y_dir = py - int(r * math.sin(robot.orientation))
            pygame.draw.line(self.screen, (255, 0, 0), (px, py), (x_dir, y_dir), 2)

        # Sinon, on retombe sur l'affichage classique (cercle bleu)
        else:
            pygame.draw.circle(self.screen, (0, 255, 0), (px, py), r, 2)
            pygame.draw.circle(self.screen, (0, 0, 255), (px, py), r - 2)
            x_dir = px + int(r * math.cos(robot.orientation))
            y_dir = py - int(r * math.sin(robot.orientation))
            pygame.draw.line(self.screen, (255, 0, 0), (px, py), (x_dir, y_dir), 2)

    def tick(self, fps=60):
        self.clock.tick(fps)

    def dessiner_environnement(self, env):
        # Effacer l'écran avec un fond clair
        self.screen.fill((245, 245, 245))

        # Dessiner les obstacles
        for obs in env.obstacles:
            obs.dessiner(self)

        # Dessiner le robot
        if env.robot:
            self.dessiner_robot(env.robot)

        pygame.display.flip()

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