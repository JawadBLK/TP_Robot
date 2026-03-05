'''
class Environnement:

    def __init__(self, largeur=30, hauteur=40):
        self.largeur = largeur
        self.hauteur = hauteur
        self.robot = None
        self.obstacles = []

    def ajouter_robot(self, robot):
        self.robot = robot

    def ajouter_obstacle(self, obstacle):
        self.obstacles.append(obstacle)

    def mettre_a_jour(self, dt):

        if self.robot is None:
            return

        # Sauvegarde ancienne position
        x_old = self.robot.x
        y_old = self.robot.y

        # Mise à jour robot
        self.robot.mettre_a_jour(dt)    

        # Vérification collisions
        for obs in self.obstacles:
            if obs.collision(self.robot.x, self.robot.y, self.robot.rayon):

            # Retour position valide
                self.robot.x = x_old
                self.robot.y = y_old

            # Stop mouvement
                self.robot.commander(v=0, omega=0)

                break   
'''
class Environnement:
    def __init__(self, largeur=20, hauteur=12):
        self.largeur = largeur
        self.hauteur = hauteur
        self.robot = None
        self.obstacles = []

    def ajouter_robot(self, robot):
        self.robot = robot
        if not hasattr(self.robot, 'rayon'):
            self.robot.rayon = 0.5 

    def ajouter_obstacle(self, obstacle):
        self.obstacles.append(obstacle)

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
