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

    def convertir_coordonnees(self, x, y):
        px = int(self.largeur / 2 + x * self.scale)
        py = int(self.hauteur / 2 - y * self.scale)
        return px, py

    def dessiner_robot(self, robot):

        x, y = self.convertir_coordonnees(robot.x, robot.y)

        r = int(robot.rayon * self.scale)

    # Cercle vert (zone collision)
        pygame.draw.circle(self.screen, (0, 255, 0), (x, y), r, 2)

    # Cercle bleu (robot)
        pygame.draw.circle(self.screen, (0, 0, 255), (x, y), r - 2)

    # Orientation
        x_dir = x + int(r * math.cos(robot.orientation))
        y_dir = y - int(r * math.sin(robot.orientation))

        pygame.draw.line(self.screen, (255, 0, 0), (x, y), (x_dir, y_dir), 2)


    def tick(self, fps=60):
        self.clock.tick(fps)

    def dessiner_environnement(self, env):

    # Effacer l'Ã©cran
        self.screen.fill((245, 245, 245))

    # Dessiner les obstacles
        for obs in env.obstacles:
            obs.dessiner(self)

    # Dessiner le robot
        self.dessiner_robot(env.robot)

        pygame.display.flip()

    def dessiner_porte(self, x, y, angle=0, largeur=2):

        px, py = self.convertir_coordonnees(x, y)
        rayon = int(largeur * self.scale)

        rect = pygame.Rect(
            px - rayon,
            py - rayon,
            2 * rayon,
            2 * rayon
        )

        pygame.draw.arc(
            self.screen,
            (100, 100, 100),
            rect,
            angle,
            angle + math.pi/2,
            2
        )