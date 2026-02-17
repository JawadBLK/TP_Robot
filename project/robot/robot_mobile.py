import math
from robot.moteur import Moteur

class RobotMobile:
    _nb_robots = 0

    def __init__(self, x, y, orientation = 0.0, moteur=None):
        self.x = x
        self.y = y
        self.orientation = orientation
        self.moteur = moteur
        # 2. On utilise la méthode statique pour valider le moteur
        if self.moteur_valide(moteur):
            self.moteur = moteur
        else:
            self.moteur = None
            print("Attention : Moteur non valide ou absent.")
            
        # 3. Incrémentation du compteur global
        RobotMobile._nb_robots += 1
    
    def __str__(self):
        return str((self.x, self.y, self.orientation))
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

    def commander(self, **kwargs):
        if self.moteur is not None:
            self.moteur.commander(**kwargs)
    
    def mettre_a_jour(self, dt):
        if self.moteur is not None:
            self.moteur.mettre_a_jour(self, dt)

    @classmethod
    def nombre_robots(cls) -> int:
        """
        Retourne le nombre total de robots crees.
        """
        return cls._nb_robots

    @staticmethod
    def moteur_valide(moteur):
        """Vérifie si l'objet est une instance de la classe Moteur."""
        # On vérifie si moteur est une instance de Moteur ou d'une de ses sous-classes
        return isinstance(moteur, Moteur)