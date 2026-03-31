import pygame
import os
import math

class Props:
    """
    Objet décoratif placé dans l'environnement.
    Peut afficher une image ou un dessin vectoriel de secours.
    """

    TYPES = {
        "bureau":    {"w": 1.2, "h": 0.6, "couleur": (139, 90,  43)},
        "chaise":    {"w": 0.4, "h": 0.4, "couleur": (160, 120, 60)},
        "plante":    {"w": 0.3, "h": 0.3, "couleur": (34,  139, 34)},
        "caisse":    {"w": 0.5, "h": 0.5, "couleur": (180, 140, 80)},
        "armoire":   {"w": 0.6, "h": 1.0, "couleur": (101, 67,  33)},
        "ordinateur":{"w": 0.5, "h": 0.4, "couleur": (50,  50,  80)},
        "lampe":     {"w": 0.2, "h": 0.2, "couleur": (255, 220, 80)},
        "tableau":   {"w": 0.8, "h": 0.5, "couleur": (200, 180, 140)},
    }

    # Cache partagé entre toutes les instances
    _image_cache = {}

    def __init__(self, x, y, type_prop="caisse", angle=0):
        self.x = x
        self.y = y
        self.angle = angle
        self.type_prop = type_prop if type_prop in self.TYPES else "caisse"
        self.info = self.TYPES[self.type_prop]
        self.w = self.info["w"]
        self.h = self.info["h"]
        self._image_surface=None


    # ─── Dessin ──────────────────────────────────────────────────────────────────

    def dessiner(self, vue):
        px, py = vue.convertir_coordonnees(self.x, self.y)
        pw = int(self.w * vue.scale)
        ph = int(self.h * vue.scale)

        if self._image_surface:
            self._dessiner_image(vue, px, py, pw, ph)
        else:
            self._dessiner_vecteur(vue, px, py, pw, ph)

    def _dessiner_image(self, vue, px, py, pw, ph):
        # Redimensionner depuis le cache
        key_size = (self._image_path, pw, ph)
        if not hasattr(self, '_scaled_cache'):
            self._scaled_cache = {}

        if key_size not in self._scaled_cache:
            self._scaled_cache[key_size] = pygame.transform.smoothscale(
                self._image_surface, (pw, ph)
            )
        img = self._scaled_cache[key_size]

        # Rotation
        if self.angle != 0:
            img = pygame.transform.rotate(img, -math.degrees(self.angle))

        rect = img.get_rect(center=(int(px), int(py)))
        vue.screen.blit(img, rect)

        # Contour
        pygame.draw.rect(vue.screen, (80, 60, 40),
                         (rect.x, rect.y, rect.width, rect.height), 1)

    def _dessiner_vecteur(self, vue, px, py, pw, ph):
        import math
        couleur      = self.info["couleur"]
        couleur_dark = tuple(max(0, c - 40) for c in couleur)

        # Rectangle orienté
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        hw, hh = pw / 2, ph / 2

        corners = [
            (-hw, -hh), ( hw, -hh),
            ( hw,  hh), (-hw,  hh)
        ]
        points = [
            (px + cx * cos_a - cy * sin_a,
             py + cx * sin_a + cy * cos_a)
            for cx, cy in corners
        ]

        pygame.draw.polygon(vue.screen, couleur, points)
        pygame.draw.polygon(vue.screen, couleur_dark, points, 2)

# ─── Collision des props ────────────────────────────────────────────────────────

    def collision(self, x, y, rayon):
        # On vérifie si le cercle (x, y, rayon) touche le rectangle du prop
        # Distance entre le centre du cercle et le rectangle
        dx = abs(x - self.x) - self.w / 2
        dy = abs(y - self.y) - self.h / 2
        
        dx = max(dx, 0)
        dy = max(dy, 0)
        
        return math.sqrt(dx*dx + dy*dy) < rayon
    # Capteur Lidar : intersection avec un rayon
    def intersection(self, ox, oy, dx, dy, max_range):
        """Calcule l'intersection avec un rayon (Lidar) en traitant le prop comme un rectangle."""
        t_min = 0.0
        t_max = max_range
        
        # Approximation : on traite le prop (même tourné) comme une boîte englobante simple pour le Lidar
        x_min = self.x - self.w / 2
        x_max = self.x + self.w / 2
        y_min = self.y - self.h / 2
        y_max = self.y + self.h / 2

        for o, d, mn, mx in ((ox, dx, x_min, x_max), (oy, dy, y_min, y_max)):
            if abs(d) < 1e-8:
                if o < mn or o > mx:
                    return None
            else:
                t1 = (mn - o) / d
                t2 = (mx - o) / d
                t1, t2 = min(t1, t2), max(t1, t2)
                t_min = max(t_min, t1)
                t_max = min(t_max, t2)
                if t_min > t_max:
                    return None
                    
        if 0 < t_min <= max_range:
            return t_min
        return None