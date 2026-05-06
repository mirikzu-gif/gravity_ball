"""Точка входа.

Сцены: MenuScene → GameScene → WinScene. Логика жизни окна и фиксированного
шага физики живёт в src.scenes.runner.run_scenes.
"""
import pygame

from src.scenes.menu import MenuScene
from src.scenes.runner import run_scenes


def main() -> None:
    # MenuScene в __init__ создаёт pygame.font.Font — pygame нужно поднять заранее.
    # run_scenes тоже вызовет pygame.init() — это идемпотентно.
    pygame.init()
    run_scenes(MenuScene())


if __name__ == "__main__":
    main()
