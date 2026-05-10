"""Tests for WorldRenderer."""
from src.rendering.world_renderer import WorldRenderer


class _Drawable:
    def __init__(self, name, calls) -> None:
        self.name = name
        self.calls = calls

    def draw(self, screen, **kwargs) -> None:
        self.calls.append((self.name, screen, kwargs))


def test_world_renderer_draws_objects_in_order():
    calls = []
    screen = object()
    sprites = object()
    platform = _Drawable("platform", calls)
    obstacle = _Drawable("obstacle", calls)
    spring = _Drawable("spring", calls)
    spike = _Drawable("spike", calls)
    goal = _Drawable("goal", calls)
    ball = _Drawable("ball", calls)
    ball_position = (10, 20)

    renderer = WorldRenderer(sprites)
    renderer.draw(
        screen,
        [platform],
        [obstacle],
        [spring],
        [spike],
        goal,
        ball,
        ball_position,
    )

    assert [call[0] for call in calls] == [
        "platform",
        "spring",
        "obstacle",
        "spike",
        "goal",
        "ball",
    ]
    assert all(call[1] is screen for call in calls)
    assert calls[0][2] == {"sprites": sprites}
    assert calls[1][2] == {"sprites": sprites}
    assert calls[2][2] == {"sprites": sprites}
    assert calls[3][2] == {"sprites": sprites}
    assert calls[4][2] == {"sprites": sprites}
    assert calls[5][2] == {
        "position": ball_position,
        "sprites": sprites,
    }
