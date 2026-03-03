import pygame

class ControleurClavierPygame:
    def __init__(self, v_max=2.0, omega_max=1.0):
        self.v_max = v_max
        self.omega_max = omega_max

    def lire_commande(self):
        """Lit les touches pressées et retourne les vitesses v et omega."""
        keys = pygame.key.get_pressed()
        v = 0.0
        omega = 0.0

        # Flèche Haut / Bas pour la vitesse linéaire (v)
        if keys[pygame.K_UP]:
            v = self.v_max
        elif keys[pygame.K_DOWN]:
            v = -self.v_max

        # Flèche Gauche / Droite pour la vitesse angulaire (omega)
        if keys[pygame.K_LEFT]:
            omega = self.omega_max
        elif keys[pygame.K_RIGHT]:
            omega = -self.omega_max

        return {"v": v, "omega": omega}