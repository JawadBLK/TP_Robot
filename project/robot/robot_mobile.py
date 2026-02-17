import math
from turtle import distance

class RobotMobile:
    def __init__(self, x, y, orientation = 0.0):
        self.x = x
        self.y = y
        self.orientation = orientation

    def avancer(self, distance):
        self.x += distance * math.cos(self.orientation)
        self.y += distance * math.sin(self.orientation)
    
    def afficher(self):
        print(f"Robot position: (x={self.x}, y={self.y}, orientation en radians= {self.orientation}, angle={math.degrees(self.orientation)}°   )")
     
    def tourner(self, angle):
        self.orientation +=  (self.orientation + angle) % (2 * math.pi)

    # Getter : Permet d'acceder a l'attribut depuis l'exterieur de la classe.
    @property
    def x(self) -> float:
        return self.__x
    # Setter : Permet la modification de l'attribut depuis l'exterieur de la classe.
    @x.setter
    def x(self, value: float):
        self.__x = value
