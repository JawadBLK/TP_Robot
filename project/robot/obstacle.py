from abc import ABC, abstractmethod
import math
import pygame

class Obstacle(ABC):

    @abstractmethod
    def collision(self, x, y, rayon_robot):
        pass

    @abstractmethod
    def dessiner(self, vue):
        pass

class ObstacleCirculaire(Obstacle):

    def __init__(self, x, y, rayon):
        self.x = x
        self.y = y
        self.rayon = rayon

    def collision(self, x_robot, y_robot, rayon_robot):
        distance = math.sqrt((self.x - x_robot)**2 + (self.y - y_robot)**2)
        return distance <= (self.rayon + rayon_robot)

    def dessiner(self, vue):  
        px, py = vue.convertir_coordonnees(self.x, self.y)
        r = int(self.rayon * vue.scale)
        pygame.draw.circle(vue.screen, (255, 0, 0), (px, py), r)

class ObstacleRectangulaire(Obstacle):

    def __init__(self, x, y, largeur, hauteur):
        self.x = x
        self.y = y
        self.largeur = largeur
        self.hauteur = hauteur

    def collision(self, x_robot, y_robot, rayon_robot):

        # Collision cercle-rectangle
        # On trouve le point le plus proche du robot sur le rectangle

        x_proche = max(self.x - self.largeur/2,
                       min(x_robot, self.x + self.largeur/2))

        y_proche = max(self.y - self.hauteur/2,
                       min(y_robot, self.y + self.hauteur/2))

        distance = math.sqrt((x_robot - x_proche)**2 +
                             (y_robot - y_proche)**2)

        return distance <= rayon_robot

    def dessiner(self, vue):

        px, py = vue.convertir_coordonnees(self.x, self.y)

        largeur_px = int(self.largeur * vue.scale)
        hauteur_px = int(self.hauteur * vue.scale)

        rect = pygame.Rect(
            px - largeur_px // 2,
            py - hauteur_px // 2,
            largeur_px,
            hauteur_px
        )

        # Remplissage mur
        pygame.draw.rect(vue.screen, (210, 210, 210), rect)

        # Contour architectural
        pygame.draw.rect(vue.screen, (120, 120, 120), rect, 2)
        
class ObstacleSegment(Obstacle):

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def collision(self, x_robot, y_robot, rayon_robot):

        # Distance point-segment
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1

        if dx == 0 and dy == 0:
            return False

        t = ((x_robot - self.x1)*dx + (y_robot - self.y1)*dy) / (dx*dx + dy*dy)
        t = max(0, min(1, t))

        x_proche = self.x1 + t*dx
        y_proche = self.y1 + t*dy

        distance = math.sqrt((x_robot - x_proche)**2 +
                             (y_robot - y_proche)**2)

        return distance <= rayon_robot

    def dessiner(self, vue):

        p1 = vue.convertir_coordonnees(self.x1, self.y1)
        p2 = vue.convertir_coordonnees(self.x2, self.y2)

        pygame.draw.line(vue.screen, (0, 255, 0), p1, p2, 3)