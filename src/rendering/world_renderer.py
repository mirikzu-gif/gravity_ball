"""Rendering orchestration for the active level world."""


class WorldRenderer:
    """Draws gameplay objects in their visual stacking order."""

    def __init__(self, sprites) -> None:
        self.sprites = sprites

    def draw(
        self,
        screen,
        platforms,
        obstacles,
        springs,
        spikes,
        goal,
        ball,
        ball_position,
    ) -> None:
        for platform in platforms:
            platform.draw(screen, sprites=self.sprites)
        for spring in springs:
            spring.draw(screen, sprites=self.sprites)
        for obstacle in obstacles:
            obstacle.draw(screen, sprites=self.sprites)
        for spike in spikes:
            spike.draw(screen, sprites=self.sprites)
        goal.draw(screen, sprites=self.sprites)
        ball.draw(screen, position=ball_position, sprites=self.sprites)
