"""Тесты state-машины JumpController.

Контроллер не зависит от pygame/pymunk — все тесты pure-Python.
"""
import pytest

from src.game.jump_controller import JumpController, JumpEvent, JumpState


MAX_T = 1.0
F = 100.0


@pytest.fixture
def controller():
    return JumpController(max_charge_time=MAX_T, jump_impulse=F)


# ---------------------------------------------------------------------------
# Конструктор и валидация
# ---------------------------------------------------------------------------


def test_initial_state_is_idle(controller):
    assert controller.state == JumpState.IDLE
    assert controller.is_charging is False
    assert controller.charge_time == 0.0
    assert controller.charge_ratio == 0.0
    assert controller.space_pressed is False


@pytest.mark.parametrize("max_t", [0, -1, -0.001])
def test_constructor_rejects_non_positive_max_charge_time(max_t):
    with pytest.raises(ValueError):
        JumpController(max_charge_time=max_t, jump_impulse=F)


@pytest.mark.parametrize("impulse", [0, -100])
def test_constructor_rejects_non_positive_impulse(impulse):
    with pytest.raises(ValueError):
        JumpController(max_charge_time=MAX_T, jump_impulse=impulse)


@pytest.mark.parametrize("min_factor", [-0.1, 1.1])
def test_constructor_rejects_invalid_min_factor(min_factor):
    with pytest.raises(ValueError):
        JumpController(max_charge_time=MAX_T, jump_impulse=F, min_factor=min_factor)


# ---------------------------------------------------------------------------
# Переходы IDLE ↔ CHARGING
# ---------------------------------------------------------------------------


def test_press_on_ground_starts_charging(controller):
    controller.press(on_ground=True)
    assert controller.state == JumpState.CHARGING
    assert controller.charge_time == 0.0
    assert controller.space_pressed is True


def test_press_in_air_does_not_start_charging(controller):
    controller.press(on_ground=False)
    assert controller.state == JumpState.IDLE
    assert controller.space_pressed is True


def test_release_from_charging_returns_jump_and_resets(controller):
    controller.press(on_ground=True)
    controller.update(0.5, on_ground=True)

    event = controller.release(on_ground=True)

    assert event is not None
    assert isinstance(event, JumpEvent)
    assert controller.state == JumpState.IDLE
    assert controller.charge_time == 0.0
    assert controller.space_pressed is False


def test_release_in_air_while_charging_no_jump(controller):
    """Если зарядился на земле, оторвался от поверхности и отпустил — прыжка нет."""
    controller.press(on_ground=True)
    controller.update(0.5, on_ground=True)

    event = controller.release(on_ground=False)

    assert event is None
    assert controller.state == JumpState.IDLE
    assert controller.charge_time == 0.0


def test_release_when_idle_returns_none(controller):
    """Отпустить пробел не нажав его — ничего не происходит."""
    event = controller.release(on_ground=True)
    assert event is None
    assert controller.state == JumpState.IDLE


def test_press_in_air_then_land_starts_charging_via_update(controller):
    """Нажал в воздухе → приземлился → в том же кадре зарядка стартует и время идёт.

    Семантика повторяет исходный game.py: автозапуск зарядки и инкремент таймера
    в одном проходе → charge_time == dt после первого update.
    """
    controller.press(on_ground=False)
    assert controller.state == JumpState.IDLE

    controller.update(0.1, on_ground=True)

    assert controller.state == JumpState.CHARGING
    assert controller.charge_time == pytest.approx(0.1)


def test_press_then_release_in_air_no_charging(controller):
    """Нажал в воздухе и отпустил в воздухе — никакой зарядки и никакого прыжка."""
    controller.press(on_ground=False)
    event = controller.release(on_ground=False)

    assert event is None
    assert controller.state == JumpState.IDLE
    assert controller.space_pressed is False


# ---------------------------------------------------------------------------
# Накопление времени зарядки
# ---------------------------------------------------------------------------


def test_charge_time_accumulates(controller):
    controller.press(on_ground=True)
    controller.update(0.3, on_ground=True)
    controller.update(0.2, on_ground=True)

    assert controller.charge_time == pytest.approx(0.5)
    assert controller.charge_ratio == pytest.approx(0.5)


def test_charge_time_is_capped_at_max(controller):
    controller.press(on_ground=True)
    controller.update(2.0, on_ground=True)  # больше MAX_T

    assert controller.charge_time == MAX_T
    assert controller.charge_ratio == 1.0


def test_charge_time_continues_off_ground():
    """Если игрок отрывается от земли, зарядка продолжает идти (исходное поведение)."""
    c = JumpController(MAX_T, F)
    c.press(on_ground=True)
    c.update(0.2, on_ground=True)
    c.update(0.3, on_ground=False)  # оторвался

    assert c.is_charging is True
    assert c.charge_time == pytest.approx(0.5)


def test_update_when_idle_does_nothing(controller):
    controller.update(0.5, on_ground=True)
    assert controller.state == JumpState.IDLE
    assert controller.charge_time == 0.0


# ---------------------------------------------------------------------------
# Формула импульса прыжка: 30% .. 100%
# ---------------------------------------------------------------------------


def test_min_impulse_at_zero_charge(controller):
    controller.press(on_ground=True)
    event = controller.release(on_ground=True)

    expected = F * 0.3
    assert event.impulse == (0.0, -expected)


def test_full_impulse_at_max_charge(controller):
    controller.press(on_ground=True)
    controller.update(MAX_T, on_ground=True)
    event = controller.release(on_ground=True)

    assert event.impulse == (0.0, -F)


def test_half_charge_gives_65_percent_impulse(controller):
    """0.3 + 0.7 * 0.5 = 0.65"""
    controller.press(on_ground=True)
    controller.update(MAX_T / 2, on_ground=True)
    event = controller.release(on_ground=True)

    expected = F * 0.65
    assert event.impulse[0] == 0.0
    assert event.impulse[1] == pytest.approx(-expected)


@pytest.mark.parametrize(
    "charge_fraction,expected_factor",
    [
        (0.0, 0.30),
        (0.25, 0.475),
        (0.5, 0.65),
        (0.75, 0.825),
        (1.0, 1.0),
    ],
)
def test_impulse_formula_linear_30_to_100(charge_fraction, expected_factor):
    c = JumpController(MAX_T, F)
    c.press(on_ground=True)
    c.update(MAX_T * charge_fraction, on_ground=True)
    event = c.release(on_ground=True)

    assert event.impulse[1] == pytest.approx(-F * expected_factor)


def test_overcharge_does_not_exceed_full_impulse(controller):
    """Если жмёшь дольше MAX_T — импульс не превышает 100%."""
    controller.press(on_ground=True)
    controller.update(MAX_T * 5, on_ground=True)
    event = controller.release(on_ground=True)

    assert event.impulse[1] == pytest.approx(-F)


# ---------------------------------------------------------------------------
# Полный цикл повторных прыжков
# ---------------------------------------------------------------------------


def test_can_jump_multiple_times(controller):
    for _ in range(3):
        controller.press(on_ground=True)
        controller.update(MAX_T, on_ground=True)
        event = controller.release(on_ground=True)
        assert event is not None
        assert controller.state == JumpState.IDLE


def test_min_factor_zero_means_no_jump_at_zero_charge():
    c = JumpController(MAX_T, F, min_factor=0.0)
    c.press(on_ground=True)
    event = c.release(on_ground=True)
    assert event.impulse[1] == pytest.approx(0.0)


def test_min_factor_one_gives_full_force_always():
    c = JumpController(MAX_T, F, min_factor=1.0)
    c.press(on_ground=True)
    event = c.release(on_ground=True)
    assert event.impulse[1] == pytest.approx(-F)
