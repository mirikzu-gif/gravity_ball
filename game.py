"""
Основной файл игры - реорганизованная версия
"""
import pygame
import pymunk
import pymunk.pygame_util

# Импорты из рефакторированных модулей
from src.entities.ball import Ball
from src.entities.obstacle import Obstacle
from src.entities.platform import Platform
from src.utils.config import (
    WIDTH, HEIGHT, GRAVITY, DAMPING, MOVE_FORCE, JUMP_FORCE, 
    MAX_CHARGE_TIME, WHITE, GRAY
)
from src.utils.physics import is_on_ground
from src.utils.level import create_level


def main():
    # Инициализация
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Упругий мяч")
    clock = pygame.time.Clock()
    
    # Физика
    space = pymunk.Space()
    space.gravity = GRAVITY
    space.damping = DAMPING
    draw_options = pymunk.pygame_util.DrawOptions(screen)
    
    # Создаем мяч
    ball = Ball(100, 100, space=space)
    
    # Создаем уровень
    obstacles, platforms = create_level(space)
    
    # Накопление силы прыжка
    jump_charge_time = 0
    jump_charging = False
    space_pressed = False  # Отслеживаем состояние пробела
    
    running = True
    keys_pressed = set()
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                keys_pressed.add(event.key)
                # Отмечаем что пробел нажат
                if event.key == pygame.K_SPACE:
                    space_pressed = True
                    # Если уже на поверхности, начинаем зарядку сразу
                    if not jump_charging and is_on_ground(ball, space):
                        jump_charging = True
                        jump_charge_time = 0
            elif event.type == pygame.KEYUP:
                keys_pressed.discard(event.key)
                # Отпускаем пробел
                if event.key == pygame.K_SPACE:
                    space_pressed = False
                    # Выполняем прыжок при отпускании пробела
                    if jump_charging:
                        jump_charging = False
                        # Проверяем, касается ли мяч поверхности
                        if is_on_ground(ball, space):
                            # Сила прыжка зависит от времени зарядки
                            charge_multiplier = min(jump_charge_time / MAX_CHARGE_TIME, 1.0)
                            actual_jump_force = JUMP_FORCE * (0.3 + 0.7 * charge_multiplier)  # От 30% до 100%
                            ball.apply_force((0, -actual_jump_force))
                        jump_charge_time = 0
        
        # Управление стрелками
        if pygame.K_LEFT in keys_pressed:
            ball.apply_force((-MOVE_FORCE, 0))
        if pygame.K_RIGHT in keys_pressed:
            ball.apply_force((MOVE_FORCE, 0))
        if pygame.K_UP in keys_pressed:
            ball.apply_force((0, -MOVE_FORCE))
        if pygame.K_DOWN in keys_pressed:
            ball.apply_force((0, MOVE_FORCE))
        
        # Автоматическая зарядка при касании поверхности если пробел зажат
        if space_pressed and not jump_charging and is_on_ground(ball, space):
            jump_charging = True
            jump_charge_time = 0
        
        # Обновление времени зарядки прыжка
        if jump_charging:
            jump_charge_time += dt
            if jump_charge_time > MAX_CHARGE_TIME:
                jump_charge_time = MAX_CHARGE_TIME
        
        # Обновление физики
        space.step(dt)
        
        # Отрисовка
        screen.fill(WHITE)
        
        # Рисуем все объекты
        for platform in platforms:
            platform.draw(screen)
        
        for obstacle in obstacles:
            obstacle.draw(screen)
        
        ball.draw(screen)
        
        # Визуальная индикация силы прыжка (только когда на поверхности)
        if jump_charging and is_on_ground(ball, space):
            charge_multiplier = jump_charge_time / MAX_CHARGE_TIME
            bar_width = 60
            bar_height = 8
            bar_x = int(ball.body.position.x - bar_width // 2)
            bar_y = int(ball.body.position.y + ball.radius + 10)
            
            # Фон полоски
            pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
            # Заполненная часть
            fill_width = int(bar_width * charge_multiplier)
            color = (255, int(255 - charge_multiplier * 200), 50)  # От желтого к красному
            pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height))
            # Рамка
            pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Информация
        font = pygame.font.Font(None, 36)
        text = font.render("Управляй мячом стрелками! Зажми пробел для зарядки прыжка", True, (0, 0, 0))
        screen.blit(text, (10, 10))
        
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    main()
