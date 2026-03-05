import math
import pygame
from abc import ABC, abstractmethod

class Obstacle(ABC):
    @abstractmethod
    def collision(self, x, y, rayon_robot):
        pass
    @abstractmethod
    def dessiner(self, vue):
        pass

class ObstacleRectangulaire(Obstacle):
    def __init__(self, x, y, largeur, hauteur, materiau="beton"):
        self.x = x
        self.y = y
        self.largeur = largeur
        self.hauteur = hauteur
        self.materiau = materiau

    def collision(self, x_robot, y_robot, rayon_robot):
        x_proche = max(self.x - self.largeur/2, min(x_robot, self.x + self.largeur/2))
        y_proche = max(self.y - self.hauteur/2, min(y_robot, self.y + self.hauteur/2))
        distance = math.sqrt((x_robot - x_proche)**2 + (y_robot - y_proche)**2)
        return distance <= rayon_robot

    def dessiner(self, vue):
        px, py = vue.convertir_coordonnees(self.x, self.y)
        largeur_px = int(self.largeur * vue.scale)
        hauteur_px = int(self.hauteur * vue.scale)

        rect = pygame.Rect(
            px - largeur_px // 2, py - hauteur_px // 2, largeur_px, hauteur_px
        )

        # NOUVELLES COULEURS PLUS RÉALISTES
        if self.materiau == "beton":
            pygame.draw.rect(vue.screen, (80, 80, 80), rect)    # Gris très foncé
        elif self.materiau == "platre":
            pygame.draw.rect(vue.screen, (180, 180, 180), rect) # Gris clair
        elif self.materiau == "bois_ferme":
            pygame.draw.rect(vue.screen, (139, 69, 19), rect)   # Marron foncé (Porte fermée)
        else:
            pygame.draw.rect(vue.screen, (200, 200, 200), rect)

        # Contour noir pour faire plan d'architecte
        pygame.draw.rect(vue.screen, (0, 0, 0), rect, 1)

class ObstaclePorte(Obstacle):
    '''def __init__(self, x, y, largeur, angle_rad=0):
        self.x = x
        self.y = y
        self.largeur = largeur
        self.angle_rad = angle_rad

    def collision(self, x_robot, y_robot, rayon_robot):
        # Une porte ouverte  bloque 
        return False

    def dessiner(self, vue):
        vue.dessiner_porte(self.x, self.y, self.angle_rad, self.largeur)'''
    def __init__(self, x, y, largeur, angle_rad=0):
        self.x = x
        self.y = y
        self.largeur = largeur
        self.angle_rad = angle_rad
        
        # On calcule les coordonnées mathématiques de l'extrémité de la porte
        self.fin_x = self.x + self.largeur * math.cos(self.angle_rad)
        self.fin_y = self.y + self.largeur * math.sin(self.angle_rad)

    def collision(self, x_robot, y_robot, rayon_robot):
        # On utilise l'algorithme de collision "Point - Segment"
        dx = self.fin_x - self.x
        dy = self.fin_y - self.y

        if dx == 0 and dy == 0:
            return False

        # Projection du centre du robot sur la ligne infinie de la porte
        t = ((x_robot - self.x) * dx + (y_robot - self.y) * dy) / (dx * dx + dy * dy)
        
        # On limite cette projection pour qu'elle reste SUR le battant de la porte [0, 1]
        t = max(0, min(1, t))

        # On trouve le point précis de la porte le plus proche du robot
        x_proche = self.x + t * dx
        y_proche = self.y + t * dy

        # On calcule la distance entre le robot et ce point
        distance = math.sqrt((x_robot - x_proche)**2 + (y_robot - y_proche)**2)

        # Si cette distance est plus petite que le rayon, BOUM, il y a collision !
        return distance <= rayon_robot

    def dessiner(self, vue):
        vue.dessiner_porte(self.x, self.y, self.angle_rad, self.largeur)

'''
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

'''
