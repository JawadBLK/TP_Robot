"""
cartographe.py
==============
Algorithme de cartographie par lancer de rayon (Raycasting).

Le Cartographe est en relation de Composition avec GrilleOccupation :
il utilise ses services (coord2index, get_cellule, set_cellule) sans
accéder directement à la matrice interne.

Utilisation :
    from grille_occupation import GrilleOccupation
    from cartographe import Cartographe
    from capteurs import Lidar

    grille = GrilleOccupation(largeur_m=20, hauteur_m=12, resolution=0.1)
    carte  = Cartographe(grille)
    lidar  = Lidar(nb_rayons=180, max_range=6.0)

    # Dans la boucle :
    carte.mise_a_jour(env, lidar)
    vue.dessiner_grille(grille)
"""

from __future__ import annotations
from .grille_occup import GrilleOccupation
from .capteurs import Lidar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Environnement import Environnement


class Cartographe:
    """
    Utilise les rayons Lidar pour mettre à jour une GrilleOccupation
    via l'algorithme de Bresenham.

    Paramètres
    ----------
    grille : instance de GrilleOccupation (composition)
    """

    def __init__(self, grille: GrilleOccupation):
        self.grille: GrilleOccupation = grille  # composition

    # ── API principale ───────────────────────────────────────────────────────

    def mise_a_jour(self, env: "Environnement", lidar: Lidar):
        """
        Récupère les rayons Lidar et applique Bresenham sur chacun.
        Chaque rayon trace des cellules LIBRES jusqu'à son point d'impact,
        puis marque ce point comme OCCUPÉ s'il n'atteint pas la portée max.
        """
        rays = lidar.get_rays_world(env)
        for x1, y1, x2, y2, dist in rays:
            self._bresenham_update(x1, y1, x2, y2, dist, lidar.max_range)

    # ── Algorithme de Bresenham ──────────────────────────────────────────────

    def _bresenham_update(
        self,
        x1: float, y1: float,
        x2: float, y2: float,
        dist: float,
        max_range: float,
    ):
        """
        Applique l'algorithme de Bresenham entre (x1,y1) et (x2,y2).

        - Toutes les cellules traversées (sauf la dernière si obstacle) → LIBRE
        - Si dist < max_range : dernière cellule → OCCUPÉ
        """
        # Convertir les extrémités en indices de grille
        ix0, iy0 = self.grille.coord2index(x1, y1)
        ix1, iy1 = self.grille.coord2index(x2, y2)

        # ── Bresenham en indices entiers ──────────────────────────────────────
        dx = abs(ix1 - ix0)
        dy = abs(iy1 - iy0)
        sx = 1 if ix0 < ix1 else -1
        sy = 1 if iy0 < iy1 else -1
        err = dx - dy

        x, y = ix0, iy0
        has_obstacle = dist < max_range - 0.05

        while True:
            # Cellule courante
            if x == ix1 and y == iy1:
                # Dernière cellule : toujours libre (les impacts sont gérés séparément)
                if self.grille.get_cellule(x, y) != GrilleOccupation.OCCUPE:
                    self.grille.set_cellule(x, y, GrilleOccupation.LIBRE)
                break

            # Cellule intermédiaire → libre (sauf si déjà marquée occupée)
            if self.grille.get_cellule(x, y) != GrilleOccupation.OCCUPE:
                self.grille.set_cellule(x, y, GrilleOccupation.LIBRE)

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x   += sx
            if e2 < dx:
                err += dx
                y   += sy