from robot.robot_mobile import RobotMobile
import math

robot = RobotMobile(0, 0, math.pi/2)
robot.afficher()
robot.avancer(1)
robot.afficher()
robot.tourner(math.pi/4)
robot.afficher()
robot.x = 10
robot.afficher()
