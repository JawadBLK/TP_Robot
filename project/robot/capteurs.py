import math
import pygame
from abc import ABC, abstractmethod

class Capteur(ABC):
    @abstractmethod
    def read(self, env): pass
    @abstractmethod
    def draw(self, vue): pass

class Lidar(Capteur):
    def __init__(self, robot, nb_rayons=180, portee_max=6.0):
        self.robot = robot
        self.nb_rayons = nb_rayons
        self.portee_max = portee_max
        self.fov = math.pi  # Champ de vision de 180° (pi en radians)
        self.mesures = []

    def read(self, env):
        self.mesures = []
        
        # L'angle de départ est à -90° (à droite) par rapport à l'avant du robot
        angle_debut = self.robot.orientation - (self.fov / 2)
        
        for i in range(self.nb_rayons):
            # On répartit uniformément les rayons sur les 180°
            if self.nb_rayons > 1:
                angle = angle_debut + (i * self.fov / (self.nb_rayons - 1))
            else:
                angle = self.robot.orientation
                
            dx = math.cos(angle)
            dy = math.sin(angle)
            
            dist_min = self.portee_max
            
            # --- 1. Tester les murs ---
            for obs in env.obstacles:
                if hasattr(obs, 'intersection'):
                    dist = obs.intersection(self.robot.x, self.robot.y, dx, dy, self.portee_max)
                    if dist is not None and dist < dist_min:
                        dist_min = dist
            
            # --- 2. Tester les props ---
            for prop in env.props:
                if hasattr(prop, 'intersection'):
                    dist = prop.intersection(self.robot.x, self.robot.y, dx, dy, self.portee_max)
                    if dist is not None and dist < dist_min:
                        dist_min = dist
                        
            # Calcul du point d'impact
            ix = self.robot.x + dist_min * dx
            iy = self.robot.y + dist_min * dy
            self.mesures.append((angle, dist_min, ix, iy))
            
        return self.mesures

    def draw(self, vue):
        px_r, py_r = vue.convertir_coordonnees(self.robot.x, self.robot.y)
        for angle, dist, ix, iy in self.mesures:
            px_i, py_i = vue.convertir_coordonnees(ix, iy)
            color = (255, 50, 50) if dist < self.portee_max else (50, 255, 50)
            pygame.draw.line(vue.screen, color, (px_r, py_r), (px_i, py_i), 1)


class CapteurThermique(Capteur):
    def __init__(self, robot, portee=15.0):
        self.robot = robot
        self.portee = portee
        self.mesures_thermiques = []

    def read(self, env):
        self.mesures_thermiques = []
        for ennemi in env.ennemis:
            dist = math.hypot(self.robot.x - ennemi.x, self.robot.y - ennemi.y)
            if dist <= self.portee:
                self.mesures_thermiques.extend(ennemi.historique_chaleur)
        return self.mesures_thermiques

    def draw(self, vue):
        surf = pygame.Surface(vue.screen.get_size(), pygame.SRCALPHA)
        
        # --- Paramètres de la grille thermique ---
        taille_pixel_m = 0.12  
        rayon_diffusion = 0.8  
        
        grille_chaleur = {}
        
        for trace in self.mesures_thermiques:
            cx, cy = trace['x'], trace['y']
            chaleur_source = trace['chaleur']
            
            min_x = int((cx - rayon_diffusion) / taille_pixel_m)
            max_x = int((cx + rayon_diffusion) / taille_pixel_m)
            min_y = int((cy - rayon_diffusion) / taille_pixel_m)
            max_y = int((cy + rayon_diffusion) / taille_pixel_m)
            
            for gx in range(min_x, max_x + 1):
                for gy in range(min_y, max_y + 1):
                    bloc_x = gx * taille_pixel_m
                    bloc_y = gy * taille_pixel_m
                    
                    dist = math.hypot(bloc_x - cx, bloc_y - cy)
                    if dist <= rayon_diffusion:
                        # Diffusion linéaire de la chaleur
                        intensite = chaleur_source * (1.0 - (dist / rayon_diffusion))
                        cle = (gx, gy)
                        grille_chaleur[cle] = max(grille_chaleur.get(cle, 0.0), intensite)

        taille_px_ecran = int(taille_pixel_m * vue.scale)
        if taille_px_ecran < 1: taille_px_ecran = 1
        
        for (gx, gy), chaleur in grille_chaleur.items():
            if chaleur <= 0.05:  # Seuil minimal pour ne pas tout dessiner
                continue
                
            # --- PALIERS DE COULEURS NETS (Pas de gradient fluide) ---
            if chaleur > 0.8:
                r, g, b = 255, 0, 0        # Rouge vif (Centre très chaud)
                alpha = 255
            elif chaleur > 0.6:
                r, g, b = 255, 255, 0      # Jaune franc
                alpha = 255
            elif chaleur > 0.4:
                r, g, b = 0, 255, 255      # Cyan/Bleu clair
                alpha = 180
            elif chaleur > 0.2:
                r, g, b = 0, 100, 255      # Bleu plus soutenu
                alpha = 120
            else:
                r, g, b = 0, 0, 150        # Bleu marine/Froid (Bords)
                alpha = 80
            
            px, py = vue.convertir_coordonnees(gx * taille_pixel_m, gy * taille_pixel_m)
            
            # -1 sur la taille pour laisser un très léger quadrillage (donne un look matrice)
            rect = pygame.Rect(px - taille_px_ecran // 2, py - taille_px_ecran // 2, taille_px_ecran - 1, taille_px_ecran - 1)
            
            pygame.draw.rect(surf, (r, g, b, alpha), rect)

        vue.screen.blit(surf, (0, 0))