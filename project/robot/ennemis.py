import math
import pygame

class Ennemi:

    def __init__(self, x, y, taille=0.6, angle=0):
        self.x = x
        self.y = y
        self.taille = taille
        self.angle = angle  # orientation en radians
        self.portee = 6     # distance vision
        self.fov = math.pi / 3  # angle vision (60°)
        self.detecte = False
        self.vitesse_rotation = 0.8  # radians par seconde

    def dessiner(self, vue):

        px, py = vue.convertir_coordonnees(self.x, self.y)
        size = self.taille * vue.scale

        # Triangle
        points = [
            (px, py - size),
            (px - size, py + size),
            (px + size, py + size)
        ]

        pygame.draw.polygon(vue.screen, (150, 215, 0), points)
        pygame.draw.polygon(vue.screen, (120, 100, 0), points, 2)

        # Dessiner cône vision
        self.dessiner_vision(vue)

    def mettre_a_jour(self, dt):
        self.angle += self.vitesse_rotation * dt

        # garder angle dans [-pi, pi]
        if self.angle > math.pi:
            self.angle -= 2 * math.pi  

    def dessiner_vision(self, vue):
        px, py = vue.convertir_coordonnees(self.x, self.y)

        start_angle = self.angle - self.fov/2
        end_angle = self.angle + self.fov/2

        points = [(px, py)]

        for a in [start_angle + i*(self.fov/30) for i in range(31)]:
            x = self.x + self.portee * math.cos(a)
            y = self.y + self.portee * math.sin(a)
            p = vue.convertir_coordonnees(x, y)
            points.append(p)

        # Couleur change selon détection
        if self.detecte:
            couleur = (255, 0, 0)
        else:
            couleur = (255, 255, 0)

        pygame.draw.polygon(vue.screen, couleur, points, 1)
    
    def mettre_a_jour(self, dt):
        self.angle += self.vitesse_rotation * dt

        # garder angle dans [-pi, pi]
        if self.angle > math.pi:
            self.angle -= 2 * math.pi   