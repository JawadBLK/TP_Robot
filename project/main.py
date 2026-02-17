from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel, MoteurOmnidirectionnel
import math

moteur_diff = MoteurDifferentiel()
moteur_omni = MoteurOmnidirectionnel()
robot = RobotMobile(0, 0, math.pi/2, moteur_diff)
robot.afficher()
robot.avancer(1)
robot.afficher()
robot.tourner(math.pi/4)
robot.afficher()
robot.x = 10
robot.afficher()

# moteur_diff = MoteurDifferentiel()
# robot = RobotMobile(moteur=moteur_diff)

dt = 1.0 # pas de temps (s)
# On doit nommer les arguments (v = ..., omega = ...) car on utilise **kwargs !
robot.commander(v = 1.0, omega = 0.0) # avance
robot.mettre_a_jour(dt)
robot.afficher()
print("Test du moteur omnidirectionnel :")
r2 = RobotMobile(0, 0, math.pi/2, moteur_omni)
r2.commander(vx = 1.0, vy = 0.0, omega = 0.0) # avance
r2.mettre_a_jour(dt)
r2.afficher()