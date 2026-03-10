import math
import pygame
import random

class Ennemi:

    def __init__(self, x, y, waypoints, taille=0.2, angle=0):
        """
        waypoints : liste de (x, y) définissant la ronde dans la salle.
                    Exemple : [(1,1), (3,1), (3,3), (1,3)] pour faire un carré. 
        """
        self.x = x
        self.y = y
        self.taille = taille
        self.angle = angle
        self.portee = 3
        self.fov = math.pi / 2  # 90° de FOV
        self.detecte = False
        self.vitesse = 0.7         # unités/seconde
        self.vitesse_rotation = 3.0 # rad/s pour tourner vers le prochain waypoint

        # Waypoints de ronde
        self.waypoints = waypoints
        self.waypoint_index = 0
        self.seuil_arrivee = 0.1    # distance pour considérer le waypoint atteint

        # Animation
        self._temps = random.uniform(0, math.pi * 2)
        self._particules = []

    # ─── Mise à jour ────────────────────────────────────────────────────────────

    def mettre_a_jour(self, dt):
        self._temps += dt

        # Waypoint cible
        cible = self.waypoints[self.waypoint_index]
        dx = cible[0] - self.x
        dy = cible[1] - self.y
        distance = math.hypot(dx, dy)

        if distance < self.seuil_arrivee:
            # Waypoint atteint → passer au suivant
            self.waypoint_index = (self.waypoint_index + 1) % len(self.waypoints)
        else:
            # Angle cible vers le waypoint
            angle_cible = math.atan2(dy, dx)

            # Rotation progressive vers l'angle cible
            diff = (angle_cible - self.angle + math.pi) % (2 * math.pi) - math.pi
            rotation = self.vitesse_rotation * dt
            if abs(diff) < rotation:
                self.angle = angle_cible
            else:
                self.angle += math.copysign(rotation, diff)

            # Garder angle dans [-pi, pi]
            if self.angle > math.pi:
                self.angle -= 2 * math.pi
            elif self.angle < -math.pi:
                self.angle += 2 * math.pi

            # Avancer vers le waypoint
            self.x += (dx / distance) * self.vitesse * dt
            self.y += (dy / distance) * self.vitesse * dt

        # Particules d'alerte
        if self.detecte and random.random() < 0.3:
            self._emettre_particule()
        for p in self._particules:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['vie'] -= dt
        self._particules = [p for p in self._particules if p['vie'] > 0]

    def _emettre_particule(self):
        angle_rand = random.uniform(0, 2 * math.pi)
        vitesse = random.uniform(0.3, 0.8)
        self._particules.append({
            'x': self.x, 'y': self.y,
            'vx': math.cos(angle_rand) * vitesse,
            'vy': math.sin(angle_rand) * vitesse,
            'vie': random.uniform(0.3, 0.7),
            'vie_max': 0.6,
            'r': random.uniform(0.03, 0.07),
        })

    # ─── Dessin ─────────────────────────────────────────────

    def dessiner(self, vue):
        self._dessiner_cone_vision(vue)
        self._dessiner_aura(vue)
        self._dessiner_corps(vue)
        self._dessiner_oeil(vue)
        self._dessiner_particules(vue)

    def _dessiner_cone_vision(self, vue):
        px, py = vue.convertir_coordonnees(self.x, self.y)
        base_color = (255, 60, 60) if self.detecte else (255, 220, 50)
        nb_couches = 6
        for i in range(nb_couches, 0, -1):
            fraction = i / nb_couches
            portee_i = self.portee * fraction
            alpha = int(30 * (1 - fraction) + 8)
            start_angle = self.angle - self.fov / 2
            points = [(px, py)]
            for j in range(31):
                a = start_angle + j * (self.fov / 30)
                wx = self.x + portee_i * math.cos(a)
                wy = self.y + portee_i * math.sin(a)
                points.append(vue.convertir_coordonnees(wx, wy))
            surf = pygame.Surface(vue.screen.get_size(), pygame.SRCALPHA)
            pygame.draw.polygon(surf, (*base_color, alpha), points)
            vue.screen.blit(surf, (0, 0))
        border_alpha = 180 if self.detecte else 120
        surf = pygame.Surface(vue.screen.get_size(), pygame.SRCALPHA)
        for offset in [-self.fov / 2, self.fov / 2]:
            ex = self.x + self.portee * math.cos(self.angle + offset)
            ey = self.y + self.portee * math.sin(self.angle + offset)
            epx, epy = vue.convertir_coordonnees(ex, ey)
            pygame.draw.line(surf, (*base_color, border_alpha), (px, py), (epx, epy), 1)
        vue.screen.blit(surf, (0, 0))

    def _dessiner_aura(self, vue):
        px, py = vue.convertir_coordonnees(self.x, self.y)
        size = self.taille * vue.scale
        pulse = 0.5 + 0.5 * math.sin(self._temps * 3)
        aura_color = (255, 80, 80) if self.detecte else (100, 200, 50)
        surf = pygame.Surface(vue.screen.get_size(), pygame.SRCALPHA)
        for ring in range(3):
            r = int(size * (1.6 + ring * 0.5 + pulse * 0.3))
            alpha = int(60 - ring * 18 - pulse * 10)
            if alpha > 0:
                pygame.draw.circle(surf, (*aura_color, alpha), (int(px), int(py)), r)
        vue.screen.blit(surf, (0, 0))

    def _dessiner_corps(self, vue):
        px, py = vue.convertir_coordonnees(self.x, self.y)
        size = self.taille * vue.scale
        pulse = 0.04 * math.sin(self._temps * 4)
        s = size * (1 + pulse)
        nb = 6
        points_outer = [(px + s * math.cos(self.angle + i * 2*math.pi/nb),
                         py + s * math.sin(self.angle + i * 2*math.pi/nb)) for i in range(nb)]
        points_inner = [(px + s*.55 * math.cos(self.angle + i * 2*math.pi/nb),
                         py + s*.55 * math.sin(self.angle + i * 2*math.pi/nb)) for i in range(nb)]
        if self.detecte:
            fill_outer, fill_inner, border_col = (200,40,40), (255,100,100), (255,200,200)
        else:
            fill_outer, fill_inner, border_col = (60,140,30), (100,200,50), (180,255,100)
        pygame.draw.polygon(vue.screen, fill_outer, points_outer)
        pygame.draw.polygon(vue.screen, fill_inner, points_inner)
        pygame.draw.polygon(vue.screen, border_col, points_outer, 2)
        a_reflet = self.angle - math.pi * 0.65
        rx = px + s * 0.35 * math.cos(a_reflet)
        ry = py + s * 0.35 * math.sin(a_reflet)
        surf = pygame.Surface(vue.screen.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255,255,255,80), (int(rx), int(ry)), max(1, int(s*0.18)))
        vue.screen.blit(surf, (0, 0))

    def _dessiner_oeil(self, vue):
        px, py = vue.convertir_coordonnees(self.x, self.y)
        size = self.taille * vue.scale
        r_blanc = max(2, int(size * 0.38))
        r_iris  = max(1, int(size * 0.24))
        r_pupil = max(1, int(size * 0.13))
        pygame.draw.circle(vue.screen, (240,240,240), (int(px), int(py)), r_blanc)
        iris_col = (220,30,30) if self.detecte else (50,180,220)
        pygame.draw.circle(vue.screen, iris_col, (int(px), int(py)), r_iris)
        pupil_x = int(px + r_iris * 0.35 * math.cos(self.angle))
        pupil_y = int(py + r_iris * 0.35 * math.sin(self.angle))
        pygame.draw.circle(vue.screen, (10,10,10), (pupil_x, pupil_y), r_pupil)
        surf = pygame.Surface(vue.screen.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255,255,255,160),
                           (int(px - r_blanc*0.3), int(py - r_blanc*0.3)),
                           max(1, int(r_blanc*0.2)))
        vue.screen.blit(surf, (0, 0))
        pygame.draw.circle(vue.screen, (30,30,30), (int(px), int(py)), r_blanc, 1)

    def _dessiner_particules(self, vue):
        surf = pygame.Surface(vue.screen.get_size(), pygame.SRCALPHA)
        for p in self._particules:
            fraction_vie = p['vie'] / p['vie_max']
            alpha = max(0, min(255, int(255 * fraction_vie)))
            r = max(1, int(p['r'] * vue.scale))
            px, py = vue.convertir_coordonnees(p['x'], p['y'])
            pygame.draw.circle(surf, (255, 80, 80, alpha), (int(px), int(py)), r)
        vue.screen.blit(surf, (0, 0))