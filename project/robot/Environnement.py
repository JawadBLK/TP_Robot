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