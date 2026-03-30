import pygame

class Cartographie:
    def __init__(self, largeur_ecran, hauteur_ecran):
        # On crée une surface noire (zones non explorées)
        self.surface = pygame.Surface((largeur_ecran, hauteur_ecran))
        self.surface.fill((0, 0, 0)) # Noir par défaut
        
    def mettre_a_jour(self, vue, lidar):
        """Peint la carte en fonction des mesures du Lidar."""
        if not lidar or not lidar.mesures:
            return

        px_robot, py_robot = vue.convertir_coordonnees(lidar.robot.x, lidar.robot.y)
        
        for angle, dist, ix, iy in lidar.mesures:
            px_impact, py_impact = vue.convertir_coordonnees(ix, iy)
            
            # 1. On trace un trait blanc épais pour marquer la zone comme "Libre"
            pygame.draw.line(self.surface, (255, 255, 255), (px_robot, py_robot), (px_impact, py_impact), 4)
            
            # 2. Si on a touché un obstacle (distance < portée max), on peint un point rouge
            if dist < lidar.portee_max:
                pygame.draw.circle(self.surface, (255, 0, 0), (int(px_impact), int(py_impact)), 3)

    def dessiner(self, screen):
        """Affiche la surface cartographiée sur l'écran principal."""
        screen.blit(self.surface, (0, 0))