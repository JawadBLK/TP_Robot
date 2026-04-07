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
        Brouillard de guerre stable sans clignotement.

        Technique : on dessine un calque noir pleine fenêtre, puis on
        perce des rectangles transparents (blend ERASE) aux endroits
        révélés par le Lidar. Les murs détectés s appuient en rouge.
        """
        # Surface de brouillard pleine fenêtre, recréée à chaque frame
        # (légère mais stable — pas de clignotement)
        fog = pygame.Surface((vue.largeur, vue.hauteur_jeu))
        fog.fill((0, 0, 0))
        fog.set_colorkey(None)

        g = self._GrilleOccupation__grid
        cell_px = max(1, int(self.resolution * vue.scale))

        # Percer les trous pour les cellules LIBRES
        libre_ixs, libre_iys = np.where(g == self.LIBRE)
        for ix, iy in zip(libre_ixs, libre_iys):
            wx = self.origin_x + (ix + 0.5) * self.resolution
            wy = self.origin_y + (iy + 0.5) * self.resolution
            px, py = vue.convertir_coordonnees(wx, wy)
            # On efface ce pixel du brouillard en le rendant transparent
            pygame.draw.rect(fog, (1, 1, 1),
                             (px - cell_px // 2, py - cell_px // 2,
                              cell_px, cell_px))

        # Rendre la couleur (1,1,1) transparente = trous dans le fog
        fog.set_colorkey((1, 1, 1))

        # Blit du brouillard (les trous laissent voir le fond en dessous)
        vue.screen.blit(fog, (0, 0))

        # Dessiner les murs détectés PAR-DESSUS le brouillard en rouge
        if alpha_fond > 0:
            occupe_ixs, occupe_iys = np.where(g == self.OCCUPE)
            for ix, iy in zip(occupe_ixs, occupe_iys):
                wx = self.origin_x + (ix + 0.5) * self.resolution
                wy = self.origin_y + (iy + 0.5) * self.resolution
                px, py = vue.convertir_coordonnees(wx, wy)
                pygame.draw.rect(vue.screen, (160, 30, 30),
                                 (px - cell_px // 2, py - cell_px // 2,
                                  cell_px, cell_px))