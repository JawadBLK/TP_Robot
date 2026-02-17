from abc import ABC, abstractmethod
from math import cos, sin
class Moteur(ABC):
    @abstractmethod
    def commander(self, *args):
        pass
    @abstractmethod
    def mettre_a_jour(self, robot, dt):
        pass


class MoteurDifferentiel(Moteur):
    def __init__(self, v=0.0, omega=0.0):
        self.v = v # vitesse linaire
        self.omega = omega # vitesse angulaire

    def commander(self, v, omega):
        self.v = v
        self.omega = omega
    
    def mettre_a_jour(self, robot, dt):
        # Mise à jour de l'orientation du robot
        robot.orientation += self.omega * dt
        
        # Mise à jour de la position du robot
        robot.x += self.v * cos(robot.orientation) * dt
        robot.y += self.v * sin(robot.orientation) * dt
    

class MoteurOmnidirectionnel(Moteur):
    def __init__(self, vx=0.0, vy=0.0, omega=0.0):
        self.vx = vx # vitesse avant
        self.vy = vy # vitesse latrale
        self.omega = omega
    
    def commander(self, vx, vy, omega):
        self.vx = vx
        self.vy = vy
        self.omega = omega
    
    def mettre_a_jour(self, robot, dt):
        # Mise à jour de l'orientation du robot
        robot.orientation += self.omega * dt
        
        # Mise à jour de la position du robot
        robot.x += (self.vx * cos(robot.orientation) - self.vy * sin(robot.orientation)) * dt
        robot.y += (self.vx * sin(robot.orientation) + self.vy * cos(robot.orientation)) * dt
