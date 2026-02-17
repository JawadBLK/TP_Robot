from abc import ABC, abstractmethod

class Controleur(ABC):
    @abstractmethod
    def lire_commande(self):
        """Retourne une commande pour le robot"""
        pass

class ControleurTerminal(Controleur):
    def lire_commande(self):
        print("Commande differentiel : v omega (ex: 1.0 0.5)")
        cmd = input("Entrez la commande : ")
        try:
            v, omega = map(float, cmd.split())
            return {'v': v, 'omega': omega}
        except ValueError:
            print("Commande invalide. Veuillez entrer deux nombres séparés par un espace.")
            return None
