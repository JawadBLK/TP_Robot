'''
from robot.obstacle import ObstacleRectangulaire

class WallSegment:
    def __init__(self, x1, y1, x2, y2, thickness=0.4):
        """
        Définit un mur par 2 points
        """
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.thickness = thickness

    def to_obstacle(self, env):
        """
        Convertit le segment en rectangle
        """
        if self.x1 == self.x2:  # Mur vertical
            height = abs(self.y2 - self.y1)
            y_center = (self.y1 + self.y2) / 2
            env.ajouter_obstacle(
                ObstacleRectangulaire(
                    self.x1,
                    y_center,
                    self.thickness,
                    height
                )
            )

        elif self.y1 == self.y2:  # Mur horizontal
            width = abs(self.x2 - self.x1)
            x_center = (self.x1 + self.x2) / 2
            env.ajouter_obstacle(
                ObstacleRectangulaire(
                    x_center,
                    self.y1,
                    width,
                    self.thickness
                )
            )

def build_plan(env):

    L = env.largeur / 2
    H = env.hauteur / 2

    walls = []

    # =========================
    # MURS EXTÉRIEURS
    # =========================

    walls.append(WallSegment(-L, -H, L, -H, 1.2))  # bas
    walls.append(WallSegment(-L, H, L, H, 1.2))    # haut
    walls.append(WallSegment(-L, -H, -L, H, 1.2))  # gauche
    walls.append(WallSegment(L, -H, L, H, 1.2))    # droite

    # =========================
    # CLOISON BUREAUX
    # =========================

    y_bureaux = 10

    # mur horizontal avec ouverture
    walls.append(WallSegment(-L, y_bureaux, -4, y_bureaux))
    walls.append(WallSegment(4, y_bureaux, L, y_bureaux))

    # murs verticaux bureaux
    walls.append(WallSegment(-8, y_bureaux, -8, H))
    walls.append(WallSegment(0, y_bureaux, 0, H))
    walls.append(WallSegment(8, y_bureaux, 8, H))

    # =========================
    # SALLE DROITE FERMÉE
    # =========================

    walls.append(WallSegment(8, H, L, H))
    walls.append(WallSegment(8, y_bureaux, 8, H))

    # =========================
    # CONVERSION EN OBSTACLES
    # =========================

    for wall in walls:
        wall.to_obstacle(env)
'''
'''
import math
from robot.obstacle import ObstacleRectangulaire, ObstaclePorte

class WallSegment:
    def __init__(self, x1, y1, x2, y2, thickness=0.4, materiau="beton"):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.thickness = thickness
        self.materiau = materiau

    def to_obstacle(self, env):
        if self.x1 == self.x2:  # Mur vertical
            height = abs(self.y2 - self.y1)
            y_center = (self.y1 + self.y2) / 2
            env.ajouter_obstacle(ObstacleRectangulaire(self.x1, y_center, self.thickness, height, self.materiau))
            
        elif self.y1 == self.y2:  # Mur horizontal
            width = abs(self.x2 - self.x1)
            x_center = (self.x1 + self.x2) / 2
            env.ajouter_obstacle(ObstacleRectangulaire(x_center, self.y1, width, self.thickness, self.materiau))

def build_plan(env):
    walls = []

    # ==========================================
    # MURS EXTÉRIEURS (Béton)
    # ==========================================
    walls.append(WallSegment(-9, -6, 9, -6, 0.4, "beton")) # Mur bas
    walls.append(WallSegment(-9, 6, 9, 6, 0.4, "beton"))   # Mur haut
    walls.append(WallSegment(9, -6, 9, 6, 0.4, "beton"))   # Mur droit
    
    # MUR GAUCHE (Découpé pour laisser l'entrée principale !)
    walls.append(WallSegment(-9, 6, -9, 1, 0.4, "beton"))
    walls.append(WallSegment(-9, -1, -9, -6, 0.4, "beton"))
    # Ajout du dessin de la porte d'entrée dans le vide créé
    env.ajouter_obstacle(ObstaclePorte(-9, -1, largeur=2.0, angle_rad=math.pi/2))

    # ==========================================
    # COULOIR CENTRAL HORIZONTAL (Plâtre)
    # ==========================================
    # Mur du haut du couloir (y = 1) - Découpé pour 2 portes
    walls.append(WallSegment(-9, 1, -3, 1, 0.2, "platre"))
    env.ajouter_obstacle(ObstaclePorte(-3, 1, largeur=1.5, angle_rad=0))
    walls.append(WallSegment(-1.5, 1, 3, 1, 0.2, "platre"))
    env.ajouter_obstacle(ObstaclePorte(3, 1, largeur=1.5, angle_rad=0))
    walls.append(WallSegment(4.5, 1, 9, 1, 0.2, "platre"))

    # Mur du bas du couloir (y = -1) - Découpé pour 2 portes
    walls.append(WallSegment(-9, -1, -3, -1, 0.2, "platre"))
    env.ajouter_obstacle(ObstaclePorte(-3, -1, largeur=1.5, angle_rad=-math.pi/2))
    walls.append(WallSegment(-1.5, -1, 3, -1, 0.2, "platre"))
    env.ajouter_obstacle(ObstaclePorte(3, -1, largeur=1.5, angle_rad=-math.pi/2))
    walls.append(WallSegment(4.5, -1, 9, -1, 0.2, "platre"))

    # ==========================================
    # SÉPARATIONS DES PIÈCES VERTICALES (Plâtre)
    # ==========================================
    # Séparations des pièces du haut
    walls.append(WallSegment(-1.5, 1, -1.5, 6, 0.2, "platre"))
    walls.append(WallSegment(4.5, 1, 4.5, 6, 0.2, "platre"))
    
    # Séparations des pièces du bas
    walls.append(WallSegment(-1.5, -1, -1.5, -6, 0.2, "platre"))
    walls.append(WallSegment(4.5, -1, 4.5, -6, 0.2, "platre"))

    for wall in walls:
        wall.to_obstacle(env)'''

import math
from robot.obstacle import ObstacleRectangulaire, ObstaclePorte

class WallSegment:
    def __init__(self, x1, y1, x2, y2, thickness=0.4, materiau="beton"):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.thickness = thickness
        self.materiau = materiau

    def to_obstacle(self, env):
        # Sécurité pour éviter les bugs si x1 > x2 ou y1 > y2
        x_min, x_max = min(self.x1, self.x2), max(self.x1, self.x2)
        y_min, y_max = min(self.y1, self.y2), max(self.y1, self.y2)

        if self.x1 == self.x2:  # Mur vertical
            height = y_max - y_min
            y_center = (y_min + y_max) / 2
            env.ajouter_obstacle(ObstacleRectangulaire(self.x1, y_center, self.thickness, height, self.materiau))
            
        elif self.y1 == self.y2:  # Mur horizontal
            width = x_max - x_min
            x_center = (x_min + x_max) / 2
            env.ajouter_obstacle(ObstacleRectangulaire(x_center, self.y1, width, self.thickness, self.materiau))

def build_plan(env):
    walls = []

    # ==========================================
    # 1. MURS EXTÉRIEURS (Béton)
    # ==========================================
    walls.append(WallSegment(-8, -5, 8, -5, 0.4, "beton"))  # Mur bas
    walls.append(WallSegment(-8, 5, 8, 5, 0.4, "beton"))    # Mur haut
    walls.append(WallSegment(8, -5, 8, 5, 0.4, "beton"))    # Mur droit
    
    # Mur gauche avec une énorme ouverture pour l'entrée (-8, de y=1 à y=-1)
    walls.append(WallSegment(-8, 5, -8, 1, 0.4, "beton"))   # Bout de mur haut-gauche
    walls.append(WallSegment(-8, -1, -8, -5, 0.4, "beton")) # Bout de mur bas-gauche

    # ==========================================
    # 2. COULOIR CENTRAL HORIZONTAL (Plâtre)
    # ==========================================
    # --- MUR DU HAUT (y=1) ---
    walls.append(WallSegment(-8, 1, -5.5, 1, 0.2, "platre"))
    # [TROU de 1.5m pour PORTE OUVERTE Haut-Gauche : x de -5.5 à -4.0]
    walls.append(WallSegment(-4.0, 1, 1.0, 1, 0.2, "platre"))
    # [TROU de 1.5m pour PORTE FERMÉE Haut-Milieu : x de 1.0 à 2.5]
    walls.append(WallSegment(2.5, 1, 8, 1, 0.2, "platre"))

    # --- MUR DU BAS (y=-1) ---
    walls.append(WallSegment(-8, -1, -5.5, -1, 0.2, "platre"))
    # [TROU de 1.5m pour PORTE OUVERTE Bas-Gauche : x de -5.5 à -4.0]
    walls.append(WallSegment(-4.0, -1, 1.0, -1, 0.2, "platre"))
    # [TROU de 1.5m pour PORTE FERMÉE Bas-Milieu : x de 1.0 à 2.5]
    walls.append(WallSegment(2.5, -1, 8, -1, 0.2, "platre"))

    # ==========================================
    # 3. CLOISONS VERTICALES (Plâtre)
    # ==========================================
    # --- CLOISONS GAUCHE (x=-2) ---
    walls.append(WallSegment(-2, 5, -2, 1, 0.2, "platre"))   # Continue en haut
    walls.append(WallSegment(-2, -1, -2, -5, 0.2, "platre")) # Continue en bas

    # --- CLOISONS DROITE (x=4) ---
    walls.append(WallSegment(4, 5, 4, 2.5, 0.2, "platre"))
    # [TROU de 1.5m pour PORTE OUVERTE Verticale : y de 2.5 à 1.0]
    
    walls.append(WallSegment(4, -1, 4, -2.5, 0.2, "platre"))
    # [TROU de 1.5m pour PORTE FERMÉE Verticale : y de -2.5 à -4.0]
    walls.append(WallSegment(4, -4.0, 4, -5, 0.2, "platre"))

    #permet de créer une collision avec le mur

    for wall in walls:
        wall.to_obstacle(env)

    # ==========================================
    # PLACEMENT DES PORTES DANS LES TROUS
    # ==========================================
    
    # --- LA GRANDE ENTRÉE (A gauche) ---
    env.ajouter_obstacle(ObstaclePorte(-8, 1, largeur=2.0, angle_rad=0))

    # --- LES 3 PORTES OUVERTES ---
    portes_ouvertes = []
    # Porte Haut-Gauche
    env.ajouter_obstacle(ObstaclePorte(-5.5, 1, largeur=1.5, angle_rad=math.pi/2))
    # Porte Bas-Gauche
    env.ajouter_obstacle(ObstaclePorte(-5.5, -1, largeur=1.5, angle_rad=-math.pi/2))
    # Porte Verticale Haut-Droite
    env.ajouter_obstacle(ObstaclePorte(4, 2.5, largeur=1.5, angle_rad=math.pi))
    # Porte verticale Bas-Milieu
    env.ajouter_obstacle(ObstaclePorte(1.0, -1, largeur=1.5, angle_rad=math.pi))


    # --- LES 3 PORTES FERMÉES ---

    portes_fermees = []
    # Porte horizontale Haut-Milieu
    portes_fermees.append(WallSegment(1.0, 1, 2.5, 1, 0.1, "bois_ferme"))

    # Porte horizontale Bas-Milieu
    #portes_fermees.append(WallSegment(1.0, -1, 2.5, -1, 0.1, "bois_ferme"))

    # Porte verticale Bas-Droite
    portes_fermees.append(WallSegment(4, -2.5, 4, -4.0, 0.1, "bois_ferme"))
    
    # permet de bloquer les portes pour les collisions
    for pf in portes_fermees:
        pf.to_obstacle(env)