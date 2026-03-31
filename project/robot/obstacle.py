import math
import pygame
from abc import ABC, abstractmethod

class Obstacle(ABC):
    """Classe abstraite pour les obstacles, avec des méthodes à implémenter pour la collision et le dessin."""
    @abstractmethod
    def collision(self, x, y, rayon_robot):
        pass
    @abstractmethod
    def dessiner(self, vue):
        pass

class ObstacleRectangulaire(Obstacle):
    """Représente un obstacle rectangulaire, comme un mur ou une cloison."""
    def __init__(self, x, y, largeur, hauteur, materiau="beton"):
        self.x = x
        self.y = y
        self.largeur = largeur
        self.hauteur = hauteur
        self.materiau = materiau

    def collision(self, x_robot, y_robot, rayon_robot):
        # On trouve le point de l'obstacle le plus proche du robot
        x_proche = max(self.x - self.largeur/2, min(x_robot, self.x + self.largeur/2))
        y_proche = max(self.y - self.hauteur/2, min(y_robot, self.y + self.hauteur/2))
        distance = math.sqrt((x_robot - x_proche)**2 + (y_robot - y_proche)**2)
        return distance <= rayon_robot

    def dessiner(self, vue):
        # On convertit les coordonnées du centre de l'obstacle en pixels pour Pygame
        px, py = vue.convertir_coordonnees(self.x, self.y)
        largeur_px = int(self.largeur * vue.scale)
        hauteur_px = int(self.hauteur * vue.scale)

        rect = pygame.Rect(
            px - largeur_px // 2, py - hauteur_px // 2, largeur_px, hauteur_px
        )

        # Couleurs différentes selon le matériau 
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

    # Méthode d'intersection pour le Lidar
    def intersection(self, ox, oy, dx, dy, max_range):
        #Calcule l'intersection avec un rayon (Lidar)
        t_min = 0.0
        t_max = max_range
        
        # Coordonnées x, y sont au centre, on calcule les bords
        x_min = self.x - self.largeur / 2
        x_max = self.x + self.largeur / 2
        y_min = self.y - self.hauteur / 2
        y_max = self.y + self.hauteur / 2

        # Algorithme d'intersection pour un rectangle
        for o, d, mn, mx in ((ox, dx, x_min, x_max), (oy, dy, y_min, y_max)):
            if abs(d) < 1e-8:
                if o < mn or o > mx:
                    return None
            else:
                t1 = (mn - o) / d
                t2 = (mx - o) / d
                t1, t2 = min(t1, t2), max(t1, t2)
                t_min = max(t_min, t1)
                t_max = min(t_max, t2)
                if t_min > t_max:
                    return None
                    
        if 0 < t_min <= max_range:
            return t_min
        return None
    
class ObstaclePorte(Obstacle):
    """Représente une porte, qui est un segment de ligne avec une certaine largeur et orientation."""
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
        
     # Méthode d'intersection pour le Lidar   
    def intersection(self, ox, oy, dx, dy, max_range):
        #Calcule l'intersection avec un rayon comme un segment paramétrique.
        ax, ay = self.x, self.y
        bx, by = self.fin_x, self.fin_y
        
        sx = bx - ax
        sy = by - ay
        
        det = dx * (-sy) - dy * (-sx)
        if abs(det) < 1e-8:
            return None # Ligne parallèle au segment
            
        inv_det = 1.0 / det
        u = ((ax - ox) * (-sy) - (ay - oy) * (-sx)) * inv_det
        t = (dx * (ay - oy) - dy * (ax - ox)) * inv_det
        
        if 0 < u <= max_range and 0 <= t <= 1:
            return u
        return None

