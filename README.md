# Gravity Ball Game

Игра с упругим мячом, управляемым стрелками, который преодолевает препятствия с помощью реалистичной физики на базе pymunk.

## Структура проекта

```
gravity_ball/
├── src/
│   ├── entities/                # Игровые сущности
│   │   ├── ball.py              # Мяч (динамическое тело)
│   │   ├── obstacle.py          # Статические препятствия (камень)
│   │   └── platform.py          # Платформы (дерево)
│   ├── game/                    # Логика игрового цикла
│   │   ├── input_handler.py     # pygame events → InputAction
│   │   ├── jump_controller.py   # State-машина зарядки прыжка
│   │   └── movement.py          # Гейтинг движения по on_ground
│   └── utils/
│       ├── config.py            # Константы и настройки
│       ├── level.py             # Генерация уровня
│       └── physics.py           # is_on_ground, custom velocity
├── tests/                       # pytest тесты (>160)
├── game.py                      # Точка входа
├── pyproject.toml               # Конфиг pytest
├── requirements.txt             # Рантайм-зависимости
└── requirements-dev.txt         # + pytest для разработки
```

## Управление

- **Стрелки** — движение мяча (только когда мяч на поверхности)
- **Пробел (зажать)** — зарядка прыжка (полоска под мячом показывает заряд)
- **Пробел (отпустить)** — выполнение прыжка с силой 30%–100%

## Особенности

- Физика с гравитацией и затуханием
- Высота прыжка зависит от времени зарядки (от 30% до 100%)
- Материальная система: мяч, камень, дерево — разные упругость/трение
- Game-loop с фиксированным шагом физики (60 Гц) и интерполяцией рендера
- В воздухе мяч летит только по инерции — стрелками управление недоступно

## Запуск

```bash
# Создать и активировать venv
python -m venv .venv
source .venv/bin/activate          # Linux/Mac
.\.venv\Scripts\Activate.ps1       # Windows PowerShell

# Установить зависимости
pip install -r requirements.txt

# Запуск
python game.py
```

## Тесты

```bash
pip install -r requirements-dev.txt
pytest
```

## Зависимости

- pygame 2.6.1
- pymunk 7.2.0

## Архитектура

### Сущности (entities/)
- **Ball** — управляемый мяч; `apply_force` для удерживаемого движения, `apply_impulse` для прыжка
- **Obstacle** — статические препятствия (камень)
- **Platform** — платформы (дерево)

### Game-loop (game/)
- **InputHandler** — преобразует pygame события в `InputAction` и трекает удерживаемые клавиши
- **JumpController** — state-машина IDLE↔CHARGING с формулой `JUMP_IMPULSE * (0.3 + 0.7 * t/T_max)`
- **movement.apply_movement_force** — применяет силу только если мяч на земле

### Утилиты (utils/)
- **config.py** — константы (`FIXED_DT`, `JUMP_FORCE`, `MATERIALS` и т.д.)
- **physics.py** — `is_on_ground` через point query, `custom_velocity_func` с air resistance
- **level.py** — статическая компоновка платформ, препятствий и стен

### Материалы

| Объект | Упругость | Трение | Масса |
|---|---|---|---|
| Мяч | 1.5 | 0.3 | 5 |
| Камень | 0.3 | 0.8 | — |
| Дерево | 0.5 | 0.9 | — |
