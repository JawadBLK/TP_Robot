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