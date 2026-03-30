"""
capteurs.py
===========
Architecture POO des capteurs pour le robot mobile.

Classes
-------
Capteur          — classe abstraite commune
Lidar            — capteur de distance 360° (raycasting)
CapteurThermique — carte thermique des ennemis par superposition gaussienne

Utilisation dans main.py :
    from capteurs import Lidar, CapteurThermique
    lidar  = Lidar(nb_rayons=180, max_range=6.0)
    thermo = CapteurThermique(resolution=0.1, sigma=0.6, decay=0.97)
    robot.capteurs = [lidar, thermo]   # ou liste libre
"""

from __future__ import annotations
import math
import random
import numpy as np
import pygame
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Environnement import Environnement


# ══════════════════════════════════════════════════════════════════════════════
#  CLASSE ABSTRAITE
# ══════════════════════════════════════════════════════════════════════════════

class Capteur(ABC):
    """Interface commune à tous les capteurs."""

    @abstractmethod
    def lire(self, env: "Environnement"):
        """Retourne l'observation brute du capteur."""
        pass

    def dessiner(self, vue, env: "Environnement"):
        """Affichage optionnel dans la vue Pygame (no-op par défaut)."""
        pass


# ══════════════════════════════════════════════════════════════════════════════
#  LIDAR
# ══════════════════════════════════════════════════════════════════════════════

class Lidar(Capteur):
    """
    Télémètre laser 2-D simulé.

    Paramètres
    ----------
    nb_rayons   : nombre de rayons (résolution angulaire)
    max_range   : portée maximale en mètres
    fov         : champ de vision en radians (2π = 360°)
    bruit_sigma : écart-type du bruit gaussien sur la distance
    """

    def __init__(
        self,
        nb_rayons: int = 180,
        max_range: float = 6.0,
        fov: float = 2 * math.pi,
        bruit_sigma: float = 0.02,
    ):
        self.nb_rayons   = nb_rayons
        self.max_range   = max_range
        self.fov         = fov
        self.bruit_sigma = bruit_sigma

        # Résultats de la dernière lecture
        self._distances: list[float] = [max_range] * nb_rayons
        self._angles:    list[float] = [0.0]       * nb_rayons

        # Carte des impacts persistants : liste de (px_monde, py_monde)
        # accumulés au fil du temps (les murs détectés restent visibles)
        self._impacts: list[tuple[float, float]] = []
        self._bruit_impact = 0.03   # bruit léger en mètres sur le point d impact

    # ── Lecture ──────────────────────────────────────────────────────────────

    def lire(self, env: "Environnement") -> list[float]:
        """
        Retourne la liste des distances mesurées pour chaque rayon.
        Met à jour self._distances et self._angles.
        """
        if env.robot is None:
            return self._distances

        rx, ry, rtheta = env.robot.x, env.robot.y, env.robot.orientation
        resultats = []

        for i in range(self.nb_rayons):
            # Angle absolu du rayon dans le repère monde
            angle = rtheta - self.fov / 2 + i * (self.fov / self.nb_rayons)
            self._angles[i] = angle

            dx = math.cos(angle)
            dy = math.sin(angle)

            dist_min = self.max_range

            # Test intersection avec chaque obstacle
            for obs in env.obstacles:
                t = self._intersecter(obs, rx, ry, dx, dy)
                if t is not None and t < dist_min:
                    dist_min = t

            # Test intersection avec chaque prop (meubles, caisses, etc.)
            for prop in env.props:
                t = self._intersect_prop(prop, ox=rx, oy=ry, dx=dx, dy=dy)
                if t is not None and t < dist_min:
                    dist_min = t

            # Bruit gaussien sur la distance
            if self.bruit_sigma > 0:
                dist_min = max(0.0, dist_min + random.gauss(0, self.bruit_sigma))

            resultats.append(dist_min)

            # Stocker le point d impact avec très léger bruit de position
            if dist_min < self.max_range - 0.05:
                bx = rx + dist_min * math.cos(angle) + random.gauss(0, self._bruit_impact)
                by = ry + dist_min * math.sin(angle) + random.gauss(0, self._bruit_impact)
                self._impacts.append((bx, by))

        self._distances = resultats
        return resultats

    def get_rays_world(self, env: "Environnement"):
        """
        Retourne les rayons sous la forme :
        [(x1, y1, x2, y2, distance), ...]
        nécessaire pour le Cartographe (algorithme de Bresenham).
        NE rappelle pas lire() — utilise les données déjà calculées ce frame.
        """
        if env.robot is None:
            return []

        rx, ry = env.robot.x, env.robot.y
        rays = []
        for angle, dist in zip(self._angles, self._distances):
            # On recule légèrement le point d impact pour tomber dans la bonne cellule
            d_impact = max(0.0, dist - 0.05)
            x2 = rx + d_impact * math.cos(angle)
            y2 = ry + d_impact * math.sin(angle)
            rays.append((rx, ry, x2, y2, dist))
        return rays

    # ── Intersection rayon / obstacle ────────────────────────────────────────

    def _intersecter(self, obs, ox, oy, dx, dy):
        """
        Dispatch vers la bonne méthode selon le type d'obstacle.
        Retourne t (distance) ou None.
        """
        # Import local pour éviter la dépendance circulaire
        from .obstacle import ObstacleRectangulaire, ObstaclePorte

        if isinstance(obs, ObstacleRectangulaire):
            return self._intersect_rect(obs, ox, oy, dx, dy)
        elif isinstance(obs, ObstaclePorte):
            return self._intersect_segment(
                ox, oy, dx, dy,
                obs.x, obs.y, obs.fin_x, obs.fin_y
            )
        return None

    def _intersect_rect(self, obs, ox, oy, dx, dy):
        """Intersection rayon / rectangle AABB (slab method)."""
        hw = obs.largeur / 2
        hh = obs.hauteur / 2
        x_min = obs.x - hw
        x_max = obs.x + hw
        y_min = obs.y - hh
        y_max = obs.y + hh

        t_min, t_max = 1e-4, self.max_range

        for o, d, mn, mx in ((ox, dx, x_min, x_max), (oy, dy, y_min, y_max)):
            if abs(d) < 1e-9:
                if o < mn or o > mx:
                    return None
            else:
                t1 = (mn - o) / d
                t2 = (mx - o) / d
                if t1 > t2:
                    t1, t2 = t2, t1
                t_min = max(t_min, t1)
                t_max = min(t_max, t2)
                if t_min > t_max:
                    return None

        return t_min if 1e-4 < t_min <= self.max_range else None

    def _intersect_segment(self, ox, oy, dx, dy, ax, ay, bx, by):
        """Intersection rayon / segment de porte."""
        sx = bx - ax
        sy = by - ay
        det = dx * (-sy) - dy * (-sx)
        if abs(det) < 1e-9:
            return None
        inv = 1.0 / det
        u = ((ax - ox) * (-sy) - (ay - oy) * (-sx)) * inv
        t = (dx * (ay - oy) - dy * (ax - ox)) * inv
        if 0 < u <= self.max_range and 0 <= t <= 1:
            return u
        return None

    def _intersect_prop(self, prop, ox, oy, dx, dy):
        """
        Intersection rayon / prop (rectangle AABB, identique aux murs).
        Les props ont attributs x, y, w, h (demi-dimensions).
        """
        x_min = prop.x - prop.w / 2
        x_max = prop.x + prop.w / 2
        y_min = prop.y - prop.h / 2
        y_max = prop.y + prop.h / 2

        t_min, t_max = 1e-4, self.max_range

        for o, d, mn, mx in ((ox, dx, x_min, x_max), (oy, dy, y_min, y_max)):
            if abs(d) < 1e-9:
                if o < mn or o > mx:
                    return None
            else:
                t1 = (mn - o) / d
                t2 = (mx - o) / d
                if t1 > t2:
                    t1, t2 = t2, t1
                t_min = max(t_min, t1)
                t_max = min(t_max, t2)
                if t_min > t_max:
                    return None

        return t_min if 1e-4 < t_min <= self.max_range else None

    def dessiner_impacts(self, vue):
        """
        Dessine tous les points d impact accumulés (murs détectés) en orange.
        À appeler PAR-DESSUS le brouillard pour que les points soient visibles.
        """
        for wx, wy in self._impacts:
            px, py = vue.convertir_coordonnees(wx, wy)
            pygame.draw.circle(vue.screen, (255, 165, 40), (px, py), 2)

    # ── Affichage rayons debug ────────────────────────────────────────────────

    def dessiner(self, vue, env: "Environnement"):
        """Dessine les rayons Lidar en vert translucide (mode debug [L])."""
        if env.robot is None:
            return
        rx, ry = env.robot.x, env.robot.y
        surf = pygame.Surface(vue.screen.get_size(), pygame.SRCALPHA)

        for angle, dist in zip(self._angles, self._distances):
            ex = rx + dist * math.cos(angle)
            ey = ry + dist * math.sin(angle)
            px1, py1 = vue.convertir_coordonnees(rx, ry)
            px2, py2 = vue.convertir_coordonnees(ex, ey)
            pygame.draw.line(surf, (100, 255, 100, 30), (px1, py1), (px2, py2), 1)

        vue.screen.blit(surf, (0, 0))


# ══════════════════════════════════════════════════════════════════════════════
#  CAPTEUR THERMIQUE
# ══════════════════════════════════════════════════════════════════════════════

class CapteurThermique(Capteur):
    """
    Caméra thermique simulée.

    Principe
    --------
    À chaque pas de temps, pour chaque ennemi présent dans l'environnement,
    on ajoute une « empreinte » gaussienne 2-D centrée sur sa position.
    Les empreintes s'accumulent dans une carte flottante (numpy) et refroidissent
    progressivement via un facteur de décroissance (decay).

    Paramètres
    ----------
    largeur_m, hauteur_m : taille du domaine en mètres
    resolution           : taille d'une cellule en mètres
    sigma                : écart-type de la gaussienne (m)
    decay                : facteur multiplicatif par pas de temps (ex. 0.97)
    intensite            : amplitude de la contribution par ennemi
    bruit_amplitude      : amplitude du bruit de mesure uniforme [-b, b]
    """

    def __init__(
        self,
        largeur_m:    float = 20.0,
        hauteur_m:    float = 12.0,
        resolution:   float = 0.15,
        sigma:        float = 0.6,
        decay:        float = 0.97,
        intensite:    float = 1.0,
        bruit_amplitude: float = 0.05,
    ):
        self.largeur_m   = largeur_m
        self.hauteur_m   = hauteur_m
        self.resolution  = resolution
        self.sigma       = sigma
        self.decay       = decay
        self.intensite   = intensite
        self.bruit_amp   = bruit_amplitude

        # Dimensions de la grille
        self.nx = int(math.ceil(largeur_m / resolution))
        self.ny = int(math.ceil(hauteur_m / resolution))

        # Origine du repère (centre de la grille = (0,0) monde)
        self.origin_x = -largeur_m / 2.0
        self.origin_y = -hauteur_m / 2.0

        # Carte de chaleur accumulée
        self._carte = np.zeros((self.nx, self.ny), dtype=np.float32)

        # Surface Pygame mise en cache
        self._surface_cache: pygame.Surface | None = None
        self._dirty = True   # faut-il recalculer la surface ?

        # Précalcul des coordonnées monde des centres de cellules
        xs = self.origin_x + (np.arange(self.nx) + 0.5) * resolution
        ys = self.origin_y + (np.arange(self.ny) + 0.5) * resolution
        self._Xgrid, self._Ygrid = np.meshgrid(xs, ys, indexing='ij')

    # ── Conversion coordonnées ───────────────────────────────────────────────

    def _monde2index(self, x: float, y: float) -> tuple[int, int]:
        ix = int((x - self.origin_x) / self.resolution)
        iy = int((y - self.origin_y) / self.resolution)
        ix = max(0, min(self.nx - 1, ix))
        iy = max(0, min(self.ny - 1, iy))
        return ix, iy

    # ── Lecture / mise à jour ────────────────────────────────────────────────

    def lire(self, env: "Environnement") -> np.ndarray:
        """
        Met à jour la carte thermique :
        1. Décroissance globale (refroidissement)
        2. Ajout d'une empreinte gaussienne pour chaque ennemi
        3. Ajout de bruit uniforme
        Retourne la carte numpy (shape nx×ny, valeurs [0, ∞)).
        """
        # 1. Refroidissement
        self._carte *= self.decay

        # 2. Empreinte gaussienne par ennemi
        inv2s2 = 1.0 / (2.0 * self.sigma ** 2)
        for ennemi in env.ennemis:
            ex, ey = ennemi.x, ennemi.y

            # Bruit de position (distribution uniforme [-1,1])
            ex += random.uniform(-1.0, 1.0) * 0.0   # bruit de mesure
            ey += random.uniform(-1.0, 1.0) * 0.0

            # Gaussienne centrée sur l'ennemi
            gauss = np.exp(
                -((self._Xgrid - ex) ** 2 + (self._Ygrid - ey) ** 2) * inv2s2
            )
            self._carte += self.intensite * gauss

        # 3. Bruit uniforme de mesure
        if self.bruit_amp > 0:
            self._carte += np.random.uniform(
                -self.bruit_amp, self.bruit_amp,
                size=self._carte.shape
            ).astype(np.float32)
            self._carte = np.clip(self._carte, 0.0, None)

        self._dirty = True
        return self._carte

    # ── Palette de couleur thermique ────────────────────────────────────────

    @staticmethod
    def _palette_thermique(t: np.ndarray) -> np.ndarray:
        """
        Convertit un tableau normalisé [0,1] en RGB thermique (froid→chaud).
        Gradient : noir → bleu → cyan → vert → jaune → rouge → blanc
        """
        t = np.clip(t, 0.0, 1.0)
        r = np.zeros_like(t)
        g = np.zeros_like(t)
        b = np.zeros_like(t)

        # Segment 0 → 0.25 : noir → bleu
        m = (t < 0.25)
        s = t[m] / 0.25
        b[m] = s

        # Segment 0.25 → 0.50 : bleu → cyan
        m = (t >= 0.25) & (t < 0.50)
        s = (t[m] - 0.25) / 0.25
        g[m] = s
        b[m] = 1.0

        # Segment 0.50 → 0.70 : cyan → vert-jaune
        m = (t >= 0.50) & (t < 0.70)
        s = (t[m] - 0.50) / 0.20
        r[m] = s
        g[m] = 1.0
        b[m] = 1.0 - s

        # Segment 0.70 → 0.90 : vert-jaune → rouge
        m = (t >= 0.70) & (t < 0.90)
        s = (t[m] - 0.70) / 0.20
        r[m] = 1.0
        g[m] = 1.0 - s

        # Segment 0.90 → 1.00 : rouge → blanc
        m = (t >= 0.90)
        s = (t[m] - 0.90) / 0.10
        r[m] = 1.0
        g[m] = s
        b[m] = s

        rgb = np.stack([r, g, b], axis=-1)
        return (rgb * 255).astype(np.uint8)

    # ── Affichage ────────────────────────────────────────────────────────────

    def dessiner(self, vue, env: "Environnement"):
        """
        Superpose la carte thermique sur la vue Pygame.
        Dessine directement en coordonnées pixels via convertir_coordonnees
        pour garantir l'alignement parfait avec les ennemis.
        """
        vmax = self._carte.max()
        if vmax < 1e-6:
            return

        t = self._carte / vmax  # normalisation [0, 1]
        rgb   = self._palette_thermique(t)   # (nx, ny, 3)
        alpha = (np.clip(t * 2.5, 0, 1) * 200).astype(np.uint8)  # (nx, ny)

        cell_px = max(1, int(self.resolution * vue.scale))

        surf = pygame.Surface(vue.screen.get_size(), pygame.SRCALPHA)

        # Itérer uniquement sur les cellules chaudes (alpha > 0) pour la perf
        chauds = np.argwhere(alpha > 5)
        for ix, iy in chauds:
            # Coordonnées monde du centre de la cellule
            wx = self.origin_x + (ix + 0.5) * self.resolution
            wy = self.origin_y + (iy + 0.5) * self.resolution
            # → pixels via la même fonction que le reste de la vue
            px, py = vue.convertir_coordonnees(wx, wy)
            r, g, b = rgb[ix, iy]
            a = int(alpha[ix, iy])
            pygame.draw.rect(surf, (int(r), int(g), int(b), a),
                             (px - cell_px // 2, py - cell_px // 2,
                              cell_px, cell_px))

        vue.screen.blit(surf, (0, 0))
        self._dessiner_legende(vue)

    def _dessiner_legende(self, vue):
        """Barre de couleur thermique + labels."""
        font = pygame.font.SysFont("Courier New", 11, bold=True)
        bw, bh = 120, 10
        bx = vue.largeur - bw - 15
        by = 12

        # Fond de la légende
        pygame.draw.rect(vue.screen, (20, 20, 30, 180), (bx - 5, by - 14, bw + 10, bh + 30))

        t_arr = np.linspace(0.0, 1.0, bw)
        colors = self._palette_thermique(t_arr)  # (bw, 3)
        for i, (r, g, b) in enumerate(colors):
            pygame.draw.line(vue.screen, (int(r), int(g), int(b)),
                             (bx + i, by), (bx + i, by + bh))

        pygame.draw.rect(vue.screen, (200, 200, 200), (bx, by, bw, bh), 1)

        lbl_froid = font.render("FROID", True, (100, 180, 255))
        lbl_chaud = font.render("CHAUD", True, (255, 80, 80))
        vue.screen.blit(lbl_froid, (bx, by + bh + 3))
        vue.screen.blit(lbl_chaud, (bx + bw - 40, by + bh + 3))


# ══════════════════════════════════════════════════════════════════════════════
#  AUTRES CAPTEURS (GPS, IMU, Bumper, Encodeurs)  — implémentations légères
# ══════════════════════════════════════════════════════════════════════════════

class GPS(Capteur):
    """Position absolue bruitée."""
    def __init__(self, bruit_sigma: float = 0.1):
        self.bruit_sigma = bruit_sigma

    def lire(self, env):
        if env.robot is None:
            return None
        return {
            "x": env.robot.x + random.gauss(0, self.bruit_sigma),
            "y": env.robot.y + random.gauss(0, self.bruit_sigma),
        }


class IMU(Capteur):
    """Centrale inertielle : orientation + vitesse angulaire + accélération."""
    def __init__(self, bruit_sigma: float = 0.01):
        self.bruit_sigma = bruit_sigma
        self._v_last = 0.0

    def lire(self, env):
        if env.robot is None:
            return None
        r = env.robot
        omega = getattr(r.moteur, 'omega', 0.0) if r.moteur else 0.0
        v     = getattr(r.moteur, 'v',     0.0) if r.moteur else 0.0
        acc   = v - self._v_last
        self._v_last = v
        return {
            "orientation":  r.orientation + random.gauss(0, self.bruit_sigma),
            "omega":        omega          + random.gauss(0, self.bruit_sigma),
            "acceleration": acc            + random.gauss(0, self.bruit_sigma),
        }


class Bumper(Capteur):
    """Détecteur de contact binaire."""
    def lire(self, env):
        if env.robot is None:
            return 0
        r = env.robot
        for obs in env.obstacles:
            if obs.collision(r.x, r.y, r.rayon + 0.05):
                return 1
        return 0


class Encodeurs(Capteur):
    """Estimation odométrique par intégration des déplacements."""
    def __init__(self):
        self._x_last = None
        self._y_last = None
        self._distance_totale = 0.0
        self._trajectoire: list[tuple[float, float]] = []

    def lire(self, env):
        if env.robot is None:
            return None
        x, y = env.robot.x, env.robot.y
        if self._x_last is None:
            self._x_last, self._y_last = x, y

        dx = x - self._x_last
        dy = y - self._y_last
        dist = math.hypot(dx, dy)
        self._distance_totale += dist
        self._trajectoire.append((x, y))
        self._x_last, self._y_last = x, y

        return {"distance_step": dist, "distance_totale": self._distance_totale}

    def dessiner(self, vue, env):
        """Trace la trajectoire parcourue."""
        if len(self._trajectoire) < 2:
            return
        surf = pygame.Surface(vue.screen.get_size(), pygame.SRCALPHA)
        pts = [vue.convertir_coordonnees(x, y) for x, y in self._trajectoire]
        pygame.draw.lines(surf, (80, 200, 255, 120), False, pts, 2)
        vue.screen.blit(surf, (0, 0))