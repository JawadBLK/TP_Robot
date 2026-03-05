import math

class Environnement:
    def __init__(self, largeur=20, hauteur=12):
        self.largeur = largeur
        self.hauteur = hauteur
        self.robot = None
        self.obstacles = []
        self.ennemis = []
        self.alerte = None
        self.temps_alerte = 0

    def ajouter_robot(self, robot):
        self.robot = robot
        if not hasattr(self.robot, 'rayon'):
            self.robot.rayon = 0.5 

    def ajouter_obstacle(self, obstacle):
        self.obstacles.append(obstacle)

    def ajouter_ennemi(self, ennemi):
        self.ennemis.append(ennemi)

    def test_collision(self, x, y, rayon):
        for obs in self.obstacles:
            if obs.collision(x, y, rayon):
                return True
        return False

    def mettre_a_jour(self, dt):
        if not self.robot:
            return

        old_x = self.robot.x
        old_y = self.robot.y

        self.robot.mettre_a_jour(dt)

        # Si le nouveau mouvement provoque une collision, on annule
        if self.test_collision(self.robot.x, self.robot.y, self.robot.rayon):
            self.robot.x = old_x
            self.robot.y = old_y

        if self.robot is None:
            return

        x_old = self.robot.x
        y_old = self.robot.y

        self.robot.mettre_a_jour(dt)

        # Gestion durée alerte
        if self.temps_alerte > 0:
            self.temps_alerte -= dt
            if self.temps_alerte <= 0:
                self.alerte = None

        # Collisions obstacles
        for obs in self.obstacles:
            if obs.collision(self.robot.x, self.robot.y, self.robot.rayon):
                self.robot.x = x_old
                self.robot.y = y_old
                self.robot.commander(v=0, omega=0)
                break

        # Collisions ennemis
        ennemi_detecte = False

        for ennemi in self.ennemis:
            ennemi.mettre_a_jour(dt)
            ennemi.detecte = False  # reset à chaque frame

            dx = self.robot.x - ennemi.x
            dy = self.robot.y - ennemi.y
            distance = math.sqrt(dx*dx + dy*dy)

            if distance <= ennemi.portee:

                angle_to_robot = math.atan2(dy, dx)
                angle_diff = (angle_to_robot - ennemi.angle + math.pi) % (2*math.pi) - math.pi

                if abs(angle_diff) <= ennemi.fov / 2:

                    blocked = False
                    for obs in self.obstacles:
                        if segment_intersect_rect(
                            ennemi.x, ennemi.y,
                            self.robot.x, self.robot.y,
                            obs
                        ):
                            blocked = True
                            break

                    if not blocked:
                        ennemi.detecte = True
                        ennemi_detecte = True

        # Alerte globale après boucle
        if ennemi_detecte:
            self.alerte = "DETECTION ENNEMI"
            self.temps_alerte = 0.5

def segment_intersect_rect(x1, y1, x2, y2, rect):
    steps = 20
    for i in range(steps + 1):
        t = i / steps
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)

        if rect.collision(x, y, 0):
            return True

    return False