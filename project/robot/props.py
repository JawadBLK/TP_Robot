import pygame
import os
import math

class Props:
    """
    Objet décoratif placé dans l'environnement.
    Peut afficher une image ou un dessin vectoriel de secours.
    """

    TYPES = {
        "bureau":    {"w": 1.2, "h": 0.6, "couleur": (139, 90,  43),  "emoji": "🗃"},
        "chaise":    {"w": 0.4, "h": 0.4, "couleur": (160, 120, 60),  "emoji": "🪑"},
        "plante":    {"w": 0.3, "h": 0.3, "couleur": (34,  139, 34),  "emoji": "🌿"},
        "caisse":    {"w": 0.5, "h": 0.5, "couleur": (180, 140, 80),  "emoji": "📦"},
        "armoire":   {"w": 0.6, "h": 1.0, "couleur": (101, 67,  33),  "emoji": "🗄"},
        "ordinateur":{"w": 0.5, "h": 0.4, "couleur": (50,  50,  80),  "emoji": "💻"},
        "lampe":     {"w": 0.2, "h": 0.2, "couleur": (255, 220, 80),  "emoji": "💡"},
        "tableau":   {"w": 0.8, "h": 0.5, "couleur": (200, 180, 140), "emoji": "🖼"},
    }

    # Cache partagé entre toutes les instances
    _image_cache = {}

    def __init__(self, x, y, type_prop="caisse", angle=0, image_path=None):
        """
        x, y        : position centre en coordonnées monde
        type_prop   : clé dans TYPES (taille + couleur de secours)
        angle       : rotation en radians
        image_path  : chemin vers une image PNG/JPG (optionnel)
        """
        self.x = x
        self.y = y
        self.angle = angle
        self.type_prop = type_prop if type_prop in self.TYPES else "caisse"
        self.info = self.TYPES[self.type_prop]
        self.w = self.info["w"]
        self.h = self.info["h"]

        # Chargement image
        self._image_path = image_path
        self._image_surface = None
        if image_path and os.path.exists(image_path):
            self._charger_image(image_path)

    # ─── Chargement image ────────────────────────────────────────────────────────

    def _charger_image(self, path):
        if path in Props._image_cache:
            self._image_surface = Props._image_cache[path]
        else:
            try:
                img = pygame.image.load(path).convert_alpha()
                Props._image_cache[path] = img
                self._image_surface = img
            except Exception as e:
                print(f"[Props] Impossible de charger '{path}' : {e}")
                self._image_surface = None

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

        # Contour subtil
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

        # Petite icône texte au centre (type abrégé)
        font_size = max(8, min(pw, ph) // 2)
        try:
            font = pygame.font.SysFont("segoeui", font_size)
        except:
            font = pygame.font.Font(None, font_size)

        label = self.type_prop[:3].upper()
        surf = font.render(label, True, (255, 255, 255))
        vue.screen.blit(surf, surf.get_rect(center=(int(px), int(py))))