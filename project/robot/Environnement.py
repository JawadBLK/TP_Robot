import math

class Environnement:
    """Représente l'environnement de jeu, gère les entités, les collisions, et les interactions."""
    def __init__(self, largeur=20, hauteur=12):
        self.largeur = largeur
        self.hauteur = hauteur
        self.robot = None
        self.obstacles = []
        self.ennemis = []
        self.alerte = None
        self.temps_alerte = 0
        self.props = []
        self.temps_debut_jeu = 0.0  # Nouveau timer pour le message de transition
        
        # --- flashbang ---
        self.temps_detection_robot = 0.0
        self.etat_partie = "EN_COURS" 
        self.temps_effet_flash = 0.0

    # ─── Ajout d'entités dans l'environnement ─────────────────────────────────────────────────────
    def ajouter_robot(self, robot):
        self.robot = robot
        if not hasattr(self.robot, 'rayon'):
            self.robot.rayon = 0.5 

    def ajouter_obstacle(self, obstacle):
        self.obstacles.append(obstacle)

    def ajouter_ennemi(self, ennemi):
        self.ennemis.append(ennemi)

    def ajouter_prop(self, prop):
        self.props.append(prop)

    # ─── Gestion des collisions ──────────────────
    def test_collision(self, x, y, rayon):
        for obs in self.obstacles:
            if obs.collision(x, y, rayon):
                return True
        for prop in self.props:          
            if prop.collision(x, y, rayon):
                return True
        return False
    # ─── Mise à jour de l'environnement ──────────────────────────

    def mettre_a_jour(self, dt):
        if not self.robot:
            return
        # --- Diminuer le timer du message de transition ---
        if self.temps_debut_jeu > 0:
            self.temps_debut_jeu -= dt

        if self.temps_effet_flash > 0:
            self.temps_effet_flash -= dt
        # --- Sauvegarder position AVANT mouvement ---
        x_old = self.robot.x
        y_old = self.robot.y

        self.robot.mettre_a_jour(dt)

        # --- Gestion durée alerte ---
        if self.temps_alerte > 0:
            self.temps_alerte -= dt
            if self.temps_alerte <= 0:
                self.alerte = None

        # --- Collisions obstacles ---
        for obs in self.obstacles:
            if obs.collision(self.robot.x, self.robot.y, self.robot.rayon):
                self.robot.x = x_old
                self.robot.y = y_old
                self.robot.commander(v=0, omega=0)
                break

        # --- Collisions props ---
        for prop in self.props:
            if prop.collision(self.robot.x, self.robot.y, self.robot.rayon):
                self.robot.x = x_old
                self.robot.y = y_old
                self.robot.commander(v=0, omega=0)
                break

        # --- Collisions ennemis et Détection ---
        ennemi_detecte = False

        for ennemi in self.ennemis:
            ennemi.mettre_a_jour(dt)
            
            # --- Si l'ennemi est stun, il ne détecte rien ---
            if hasattr(ennemi, 'temps_stun') and ennemi.temps_stun > 0:
                continue 
                
            ennemi.detecte = False

            dx = self.robot.x - ennemi.x
            dy = self.robot.y - ennemi.y
            distance = math.sqrt(dx*dx + dy*dy)

            # L'ennemi peut détecter le robot s'il est dans sa portée et dans son champ de vision
            if distance <= ennemi.portee:
                angle_to_robot = math.atan2(dy, dx)
                angle_diff = (angle_to_robot - ennemi.angle + math.pi) % (2*math.pi) - math.pi
            # Si le robot est dans le champ de vision de l'ennemi, on vérifie s'il n'y a pas d'obstacle entre eux
                if abs(angle_diff) <= ennemi.fov / 2:
                    blocked = False
                    for obs in self.obstacles:
                        if segment_intersect_rect(ennemi.x, ennemi.y, self.robot.x, self.robot.y, obs):
                            blocked = True
                            break
                    if not blocked:
                        ennemi.detecte = True
                        ennemi_detecte = True

        # --- CONDITIONS DE FIN DE JEU ---
        if ennemi_detecte:
            self.temps_detection_robot += dt
            self.alerte = "DETECTION ENNEMI"
            self.temps_alerte = 0.2
            
            # --- CONDITION D'ÉCHEC (Détecté pendant 3 secondes continues)
            if self.temps_detection_robot >= 3.0:
                self.etat_partie = "ECHEC"
        else:
            self.temps_detection_robot = 0.0 # On se cache, le compteur retombe à zéro

        # --- CONDITION DE VICTOIRE (Tous les ennemis sont stun) ---
        if len(self.ennemis) > 0 and all(hasattr(e, 'temps_stun') and e.temps_stun > 0 for e in self.ennemis):
            self.etat_partie = "VICTOIRE"

# ─── Flashbang : Étourdir les ennemis proches ─────────────────────────────────────────────
    def lancer_flashbang(self, portee=3.0):
        """Étourdit les ennemis proches (s'il n'y a pas de mur entre eux et le robot)."""
        if self.etat_partie != "EN_COURS":
            return
        self.temps_effet_flash = 0.6   # Durée de l'effet flashbang affichage (en secondes) 
        for ennemi in self.ennemis:
            dist = math.hypot(self.robot.x - ennemi.x, self.robot.y - ennemi.y)
            if dist <= portee:
                # Vérification de la ligne de vue (le flashbang ne traverse pas les murs pleins)
                blocked = False
                for obs in self.obstacles:
                    if segment_intersect_rect(ennemi.x, ennemi.y, self.robot.x, self.robot.y, obs):
                        blocked = True
                        break
                if not blocked:
                    ennemi.temps_stun = 120.0  # 2 minutes de stun !

# ─── Fonction utilitaire pour vérifier l'intersection d'un segment avec un rectangle (obstacle) ─────────────────────────────────────────────
def segment_intersect_rect(x1, y1, x2, y2, rect):
    steps = 20
    for i in range(steps + 1):
        t = i / steps
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)

        if rect.collision(x, y, 0):
            return True

    return False