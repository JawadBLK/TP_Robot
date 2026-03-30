"""
grille_occupation.py
====================
Structure de données 2-D pour la cartographie d'occupation.

États des cellules
------------------
  -1  → Inconnu   (valeur initiale)
   0  → Libre     (rayon Lidar passé sans obstacle)
   1  → Occupé    (rayon Lidar a heurté un obstacle)

La grille est encapsulée : seules les méthodes coord2index / get_cellule /
set_cellule permettent d'y accéder depuis l'extérieur.
"""

from __future__ import annotations
import math
import numpy as np
import pygame


class GrilleOccupation:
    """
    Mémoire spatiale discrète du robot.

    Paramètres
    ----------
    largeur_m   : largeur du domaine en mètres
    hauteur_m   : hauteur du domaine en mètres
    resolution  : taille d'une cellule en mètres (ex. 0.1)
    """

    INCONNU = -1
    LIBRE   =  0
    OCCUPE  =  1

    def __init__(
        self,
        largeur_m:  float = 20.0,
        hauteur_m:  float = 12.0,
        resolution: float = 0.1,
    ):
        self.largeur_m  = largeur_m
        self.hauteur_m  = hauteur_m
        self.resolution = resolution

        # Nombre de cellules
        self.nx = int(math.ceil(largeur_m / resolution))
        self.ny = int(math.ceil(hauteur_m / resolution))

        # Origine du repère monde → coin bas-gauche de la grille
        self.origin_x = -largeur_m / 2.0
        self.origin_y = -hauteur_m / 2.0

        # Matrice privée initialisée à INCONNU
        self.__grid = np.full((self.nx, self.ny), self.INCONNU, dtype=np.int8)

        # Cache de la surface Pygame
        self._surface_cache: pygame.Surface | None = None
        self._dirty = True

    # ── Conversions ──────────────────────────────────────────────────────────

    def coord2index(self, x: float, y: float) -> tuple[int, int]:
        """
        Convertit des coordonnées monde (mètres) en indices de grille.
        Les indices sont bridés (clip) pour rester dans les bornes.
        """
        ix = int((x - self.origin_x) / self.resolution)
        iy = int((y - self.origin_y) / self.resolution)
        ix = max(0, min(self.nx - 1, ix))
        iy = max(0, min(self.ny - 1, iy))
        return ix, iy

    # ── Accesseurs encapsulés ────────────────────────────────────────────────

    def get_cellule(self, ix: int, iy: int) -> int:
        """Retourne l'état de la cellule (ix, iy)."""
        return int(self.__grid[ix, iy])

    def set_cellule(self, ix: int, iy: int, etat: int):
        """Modifie l'état de la cellule (ix, iy) et invalide le cache."""
        if self.__grid[ix, iy] != etat:
            self.__grid[ix, iy] = etat
            self._dirty = True

    # ── Propriétés de lecture (numpy, pas d'écriture directe) ───────────────

    @property
    def shape(self) -> tuple[int, int]:
        return self.nx, self.ny

    # ── Affichage Pygame ─────────────────────────────────────────────────────

    def dessiner(self, vue, alpha_fond: int = 220):
        """
        Brouillard de guerre : toute la fenêtre est noire au départ.
        Le Lidar révèle progressivement les zones explorées.

        Couleurs :
          - Inconnu  → noir opaque  (jamais vu)
          - Libre    → transparent  (zone révélée)
          - Occupé   → rouge foncé  (mur/obstacle détecté)
        """
        # 1. Recouvrir toute la fenêtre en noir opaque
        fog = pygame.Surface((vue.largeur, vue.hauteur_jeu), pygame.SRCALPHA)
        fog.fill((0, 0, 0, 255))
        vue.screen.blit(fog, (0, 0))

        # 2. Creuser des trous transparents dans le brouillard
        #    pour les cellules révélées par le Lidar
        if self._dirty:
            self._surface_cache = self._construire_surface(vue, alpha_fond)
            self._dirty = False

        if self._surface_cache is None:
            return

        px0, py0 = vue.convertir_coordonnees(
            self.origin_x,
            self.origin_y + self.hauteur_m,
        )
        vue.screen.blit(self._surface_cache, (px0, py0))

    def _construire_surface(self, vue, alpha_fond: int) -> pygame.Surface:
        cell_px = max(1, int(self.resolution * vue.scale))
        W = self.nx * cell_px
        H = self.ny * cell_px

        # Grille RGBA via numpy : construction vectorisée
        g = self._GrilleOccupation__grid  # accès au nom mangled

        # Tableaux RGBA (nx, ny, 4) — initialisation noire opaque (inconnu)
        rgba = np.zeros((self.nx, self.ny, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255  # tout opaque par défaut (brouillard noir)

        # Cellules LIBRES → transparentes (révélées, on voit le fond)
        libre = (g == self.LIBRE)
        rgba[libre, 0] = 0
        rgba[libre, 1] = 0
        rgba[libre, 2] = 0
        rgba[libre, 3] = 0   # transparent = zone découverte

        # Cellules OCCUPÉES → rouge foncé opaque (obstacle détecté)
        occupe = (g == self.OCCUPE)
        rgba[occupe, 0] = 160
        rgba[occupe, 1] = 30
        rgba[occupe, 2] = 30
        rgba[occupe, 3] = alpha_fond

        # Construction surface : make_surface attend RGB puis on injecte alpha
        surf_rgb = pygame.surfarray.make_surface(rgba[:, :, :3])
        alpha_surf = surf_rgb.convert_alpha()
        pxa = pygame.surfarray.pixels_alpha(alpha_surf)
        pxa[:, :] = rgba[:, :, 3]
        del pxa

        # Inverser Y (Pygame Y=0 en haut, monde Y=0 en bas)
        alpha_surf = pygame.transform.flip(alpha_surf, False, True)

        # Zoom vers la taille écran
        surf_big = pygame.transform.scale(alpha_surf, (W, H))
        return surf_big