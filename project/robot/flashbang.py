"""
flashbang.py
============
Système de flashbang pour neutraliser temporairement les ennemis.

Comportement
------------
- Le robot lance une flashbang via la barre espace
- Tous les ennemis dans le rayon d'effet sont aveuglés :
    → leur FOV est réduit à 0 (ne peuvent plus détecter le robot)
    → leur vitesse est réduite pendant l'étourdissement
- Effet visuel : flash blanc intense qui s'estompe + cercle d'onde de choc
- Temps de recharge avant de pouvoir relancer

Intégration dans main.py
------------------------
    from robot.flashbang import Flashbang

    flashbang = Flashbang(rayon=4.0, duree_effet=3.0, recharge=5.0)

    # Dans la boucle événements :
    elif event.key == pygame.K_SPACE:
        flashbang.lancer(env)

    # Dans la boucle mise à jour :
    flashbang.mettre_a_jour(dt)

    # Dans la boucle rendu (avant HUD) :
    flashbang.dessiner(vue)
"""

from __future__ import annotations
import math
import pygame
from typing import TYPE_CHECKING
from .Environnement import segment_intersect_rect

if TYPE_CHECKING:
    from .Environnement import Environnement


class Flashbang:
    """
    Gère le lancer de flashbang et ses effets sur les ennemis.

    Paramètres
    ----------
    rayon       : rayon d'effet en mètres
    duree_effet : durée d'aveuglement des ennemis (secondes)
    recharge    : temps de recharge entre deux lancers (secondes)
    """

    def __init__(
        self,
        rayon:       float = 4.0,
        duree_effet: float = 3.0,
        recharge:    float = 5.0,
    ):
        self.rayon       = rayon
        self.duree_effet = duree_effet
        self.recharge    = recharge

        # État interne
        self._cooldown      = 0.0   # temps restant avant rechargement
        self._flash_timer   = 0.0   # durée restante du flash blanc écran
        self._flash_duree   = 0.4   # durée totale du flash visuel (s)
        self._onde_timer    = 0.0   # durée restante de l'onde de choc
        self._onde_duree    = 0.5   # durée de l'animation de l'onde (s)
        self._onde_pos      = None  # position (x, y) monde du dernier lancer
        self._pret          = True  # peut-on lancer ?

        # Sauvegarde des stats originales des ennemis touchés
        # { ennemi : (fov_original, vitesse_originale, temps_restant) }
        self._ennemis_aveuglés: dict = {}

    # ── Lancer ───────────────────────────────────────────────────────────────

    def lancer(self, env: "Environnement"):
        """
        Lance la flashbang depuis la position du robot.
        Sans effet si en recharge.
        """
        if not self._pret or env.robot is None:
            return

        rx, ry = env.robot.x, env.robot.y

        # Déclencher les effets visuels
        self._flash_timer = self._flash_duree
        self._onde_timer  = self._onde_duree
        self._onde_pos    = (rx, ry)

        # Appliquer l'aveuglement aux ennemis dans le rayon
        for ennemi in env.ennemis:
            dx = ennemi.x - rx
            dy = ennemi.y - ry
            dist = math.hypot(dx, dy)

            if dist <= self.rayon:
                # Vérifier la ligne de vue : la flashbang ne traverse pas les murs
                bloque = False
                for obs in env.obstacles:
                    if segment_intersect_rect(rx, ry, ennemi.x, ennemi.y, obs):
                        bloque = True
                        break
                if bloque:
                    continue

                # Sauvegarder les stats si pas déjà aveuglé
                if ennemi not in self._ennemis_aveuglés:
                    self._ennemis_aveuglés[ennemi] = {
                        "fov":              ennemi.fov,
                        "vitesse":          ennemi.vitesse,
                        "vitesse_rotation": ennemi.vitesse_rotation,
                    }

                # Intensité selon la distance (plus proche = effet max)
                intensite = 1.0 - (dist / self.rayon)
                duree_reelle = self.duree_effet * (0.5 + 0.5 * intensite)

                # Marquer l ennemi comme neutralisé via un flag dédié
                ennemi.aveugle = True
                ennemi.detecte = False

                # Stocker le timer d'aveuglement
                self._ennemis_aveuglés[ennemi]["timer"] = duree_reelle

        # Démarrer le cooldown
        self._cooldown = self.recharge
        self._pret     = False

    # ── Mise à jour ──────────────────────────────────────────────────────────

    def mettre_a_jour(self, dt: float):
        """
        Met à jour les timers : cooldown, flash visuel, récupération des ennemis.
        À appeler à chaque frame.
        """
        # Cooldown de recharge
        if not self._pret:
            self._cooldown -= dt
            if self._cooldown <= 0:
                self._cooldown = 0.0
                self._pret     = True

        # Flash visuel
        if self._flash_timer > 0:
            self._flash_timer -= dt

        # Onde de choc
        if self._onde_timer > 0:
            self._onde_timer -= dt

        # Récupération des ennemis aveuglés
        a_retirer = []
        for ennemi, stats in self._ennemis_aveuglés.items():
            stats["timer"] -= dt
            if stats["timer"] <= 0:
                # Restaurer les stats et lever le flag
                ennemi.fov              = stats["fov"]
                ennemi.vitesse          = stats["vitesse"]
                ennemi.vitesse_rotation = stats["vitesse_rotation"]
                ennemi.aveugle          = False
                a_retirer.append(ennemi)

        for ennemi in a_retirer:
            del self._ennemis_aveuglés[ennemi]

    # ── Affichage ────────────────────────────────────────────────────────────

    def dessiner_ennemis_neutralises(self, vue, env):
        """
        Dessine un halo rouge clignotant sur les ennemis neutralisés.
        À appeler PAR-DESSUS le brouillard.
        """
        ticks = pygame.time.get_ticks()
        for ennemi in env.ennemis:
            if not getattr(ennemi, "aveugle", False):
                continue
            # Récupérer le timer restant pour fade-out
            stats = self._ennemis_aveuglés.get(ennemi, {})
            timer = stats.get("timer", 0)
            fraction = min(1.0, timer / self.duree_effet)

            # Clignotement : fréquence augmente quand le temps expire
            freq = 4 + (1 - fraction) * 8   # Hz : 4 → 12
            cligno = (math.sin(ticks * 0.001 * freq * math.pi * 2) > 0)

            px, py = vue.convertir_coordonnees(ennemi.x, ennemi.y)
            r = int(ennemi.taille * vue.scale)

            surf = pygame.Surface(vue.screen.get_size(), pygame.SRCALPHA)
            alpha = int(180 * fraction) if cligno else 0

            # Halo rouge
            pygame.draw.circle(surf, (255, 30, 30, alpha), (px, py), r * 3)
            # Croix centrale
            if cligno:
                pygame.draw.circle(surf, (255, 80, 80, min(255, alpha + 50)),
                                   (px, py), r, 2)
                # Texte STUNNED
                font = pygame.font.SysFont("Courier New", 10, bold=True)
                txt = font.render("STUNNED", True, (255, 60, 60))
                vue.screen.blit(txt, (px - txt.get_width() // 2, py - r * 3 - 14))

            vue.screen.blit(surf, (0, 0))

    def dessiner(self, vue):
        """
        Dessine les effets visuels de la flashbang :
        - Flash blanc plein écran qui s'estompe
        - Onde de choc circulaire depuis la position du lancer
        - Indicateur de recharge en bas
        """
        # ── Flash blanc écran ─────────────────────────────────────────────────
        if self._flash_timer > 0:
            fraction = self._flash_timer / self._flash_duree
            # Courbe exponentielle : très intense au début, vite estompé
            alpha = int(255 * (fraction ** 0.4))
            flash_surf = pygame.Surface(
                (vue.largeur, vue.hauteur_jeu), pygame.SRCALPHA
            )
            flash_surf.fill((255, 255, 220, alpha))
            vue.screen.blit(flash_surf, (0, 0))

        # ── Onde de choc ─────────────────────────────────────────────────────
        if self._onde_timer > 0 and self._onde_pos is not None:
            fraction = 1.0 - (self._onde_timer / self._onde_duree)
            rayon_px  = int(self.rayon * vue.scale * fraction)
            alpha_onde = int(200 * (1.0 - fraction))

            px, py = vue.convertir_coordonnees(*self._onde_pos)
            onde_surf = pygame.Surface(
                (vue.largeur, vue.hauteur_jeu), pygame.SRCALPHA
            )
            # Cercle extérieur blanc
            if rayon_px > 0:
                pygame.draw.circle(
                    onde_surf, (255, 255, 200, alpha_onde),
                    (px, py), rayon_px, max(2, int(rayon_px * 0.08))
                )
            vue.screen.blit(onde_surf, (0, 0))

        # ── Indicateur de recharge (barre en bas à droite) ───────────────────
        self._dessiner_hud(vue)

    def _dessiner_hud(self, vue):
        """Barre de recharge + icône flashbang."""
        font  = pygame.font.SysFont("Courier New", 12, bold=True)
        bw, bh = 100, 8
        bx = vue.largeur - bw - 100   # à gauche du compteur FPS
        by = vue.hauteur_jeu + 10

        # Fond de la barre
        pygame.draw.rect(vue.screen, (30, 30, 40), (bx, by + 14, bw, bh), border_radius=3)

        if self._pret:
            # Prêt : barre pleine verte
            pygame.draw.rect(vue.screen, (80, 220, 80), (bx, by + 14, bw, bh), border_radius=3)
            label = font.render("FLASH  PRÊT", True, (80, 220, 80))
        else:
            # En recharge : barre qui se remplit
            fraction = 1.0 - (self._cooldown / self.recharge)
            fill_w   = int(bw * fraction)
            col      = (
                int(220 * (1 - fraction) + 80 * fraction),
                int(80  * (1 - fraction) + 220 * fraction),
                50
            )
            if fill_w > 0:
                pygame.draw.rect(vue.screen, col, (bx, by + 14, fill_w, bh), border_radius=3)
            secs = max(0.0, self._cooldown)
            label = font.render(f"FLASH  {secs:.1f}s", True, (180, 120, 40))

        pygame.draw.rect(vue.screen, (80, 80, 100), (bx, by + 14, bw, bh), 1, border_radius=3)

        # Touche [ESPACE]
        label_key = font.render("[ESPACE]", True, (120, 120, 160))
        vue.screen.blit(label_key, (bx, by))
        vue.screen.blit(label,     (bx, by + 24))

    # ── Propriétés utiles ────────────────────────────────────────────────────

    @property
    def pret(self) -> bool:
        """True si la flashbang peut être lancée."""
        return self._pret

    @property
    def nb_ennemis_aveuglés(self) -> int:
        """Nombre d'ennemis actuellement aveuglés."""
        return len(self._ennemis_aveuglés)