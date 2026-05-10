"""
Класс мяча
"""
import math

import pygame
import pymunk

from ..utils import assets, skins
from ..utils.config import MATERIALS


class Ball:
    def __init__(self, x, y, radius=20, space=None):
        self.radius = radius
        self.space = space

        material = MATERIALS['ball']
        self.mass = material['mass']
        self.elasticity = material['elasticity']

        moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, moment)
        self.body.position = x, y

        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = self.elasticity
        self.shape.friction = material['friction']

        if space:
            space.add(self.body, self.shape)

    def apply_force(self, force):
        """Применяет силу к мячу (действует один шаг space.step)."""
        self.body.apply_force_at_world_point(force, self.body.position)

    def apply_torque(self, torque):
        """Применяет крутящий момент к мячу на один шаг space.step."""
        self.body.torque += torque

    def apply_impulse(self, impulse):
        """Применяет мгновенный импульс — изменяет velocity сразу, не зависит от dt."""
        self.body.apply_impulse_at_world_point(impulse, self.body.position)

    def draw(self, screen, position=None, sprites=None):
        """Рисует мяч. position позволяет передать интерполированную позицию для рендера.

        Если в assets/ball.png есть спрайт подходящего размера — используется он;
        иначе fallback на простой круг.
        """
        if position is None:
            position = self.body.position
        if sprites is None:
            sprites = assets.get_sprite_manager()

        skin = skins.get_selected_skin()
        sprite = sprites.get_scaled(
            skin.sprite_id,
            (self.radius * 2, self.radius * 2),
        )
        if sprite is None and skins.get_selected_index() == skins.DEFAULT_SKIN_INDEX:
            sprite = sprites.get_scaled(
                "ball",
                (self.radius * 2, self.radius * 2),
            )

        if sprite is not None:
            rotated = self._rotate_surface(sprite)
            rect = rotated.get_rect(center=(int(position[0]), int(position[1])))
            screen.blit(rotated, rect)
            return

        sprite = self._make_skin_surface(skin)
        rotated = self._rotate_surface(sprite)
        rect = rotated.get_rect(center=(int(position[0]), int(position[1])))
        screen.blit(rotated, rect)

    def _rotate_surface(self, surface):
        if abs(self.body.angle) < 0.001:
            return surface
        return pygame.transform.rotate(surface, -math.degrees(self.body.angle))

    def _make_skin_surface(self, skin):
        diameter = self.radius * 2
        surface = pygame.Surface((diameter + 4, diameter + 4), pygame.SRCALPHA)
        center = (surface.get_width() // 2, surface.get_height() // 2)
        radius = self.radius

        shade_pos = (center[0] - radius // 5, center[1] + radius // 5)
        pygame.draw.circle(surface, skin.shade, center, radius)
        pygame.draw.circle(surface, skin.fill, shade_pos, max(2, radius - 4))

        highlight_pos = (
            center[0] - radius // 3,
            center[1] - radius // 3,
        )
        pygame.draw.circle(
            surface,
            skin.highlight,
            highlight_pos,
            max(2, radius // 3),
        )
        pygame.draw.line(
            surface,
            skin.outline,
            (center[0] + radius // 3, center[1]),
            (center[0] + radius - 5, center[1]),
            3,
        )
        pygame.draw.circle(surface, skin.outline, center, radius, 2)
        return surface
