import math
import pygame


class VueTerminal:
    def dessiner_robot(self, robot):
        """
        Affiche les informations du robot de manière lisible dans le terminal.
        """
        print("\n=== État du Robot ===")
        # On accède aux attributs du modèle (le robot)
        print(f"Position    : x = {robot.x:.2f}, y = {robot.y:.2f}")
        print(f"Orientation : {robot.orientation:.2f} rad")
        
        if robot.moteur:
            print(f"Moteur      : {type(robot.moteur).__name__}")
        else:
            print("Moteur      : Aucun")
        print("=====================\n")


class VuePygame:
    def __init__(self, largeur=800, hauteur=600, scale=50):
        pygame.init()
        self.screen = pygame.display.set_mode((largeur, hauteur))
        pygame.display.set_caption("Simulation de Robot Mobile")
        self.largeur = largeur
        self.hauteur = hauteur
        self.scale = scale # metres -> pixels
        self.clock = pygame.time.Clock()

    def convertir_coordonnees(self, x, y):
        px = int(self.largeur / 2 + (x * self.scale))
        py = int(self.hauteur / 2 - (y * self.scale))
        return px, py
    
    def dessiner_robot(self, robot):
        self.screen.fill((240, 240, 240)) # rempli l'ecran de blanc
        x, y = self.convertir_coordonnees(robot.x, robot.y)
        r = 10 # rayon du robot en pixels
        pygame.draw.circle(self.screen, (0, 100, 255), (x, y), r) # dessine le robot
        x_dir = x + int(r * math.cos(robot.orientation))
        y_dir = y - int(r * math.sin(robot.orientation))
        pygame.draw.line(self.screen, (255, 0, 0), (x, y), (x_dir, y_dir), 2) # dessine la direction
        pygame.display.flip() # met a jour l'affichage

    def tick(self, fps=60):
        self.clock.tick(fps)


        