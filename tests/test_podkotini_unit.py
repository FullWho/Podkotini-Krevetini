"""Авторские модульные тесты (AAA). ID соответствует TEST_CASES.md."""
import math
import unittest

from podkotini_krevetini import (
    PodkotiniKrevetini,
    PodkotiniImmobilized,
    PodkotiniNoEnergy,
    PodkotiniTooDeep,
)


def craft(**overrides):
    args = dict(name="Подкотини Креветини", mass_kg=250.0, tail_span_m=1.8,
                max_speed_kmh=40.0, max_depth_m=200.0)
    args.update(overrides)
    return PodkotiniKrevetini(**args)


class TestPodkotiniUnit(unittest.TestCase):
    def test_tc_01_empty_name(self):
        """TC-01: Имя не может быть пустым после strip."""
        with self.assertRaises(ValueError):
            craft(name="  ")

    def test_tc_02_zero_mass(self):
        """TC-02: Масса должна быть положительной."""
        with self.assertRaises(ValueError):
            craft(mass_kg=0)

    def test_tc_03_negative_tail_span(self):
        """TC-03: Неположительный хвост запрещён."""
        with self.assertRaises(ValueError):
            craft(tail_span_m=-1)

    def test_tc_04_zero_speed(self):
        """TC-04: Скорость должна быть больше нуля."""
        with self.assertRaises(ValueError):
            craft(max_speed_kmh=0)

    def test_tc_05_zero_max_depth(self):
        """TC-05: Предел глубины должен быть больше нуля."""
        with self.assertRaises(ValueError):
            craft(max_depth_m=0)

    def test_tc_06_energy_out_of_range(self):
        """TC-06: Энергия не может быть больше 100."""
        with self.assertRaises(ValueError):
            craft(energy=101)

    def test_tc_07_negative_integrity(self):
        """TC-07: Целостность от 0 до 100."""
        with self.assertRaises(ValueError):
            craft(hull_integrity=-1)

    def test_tc_08_bool_not_numeric(self):
        """TC-08: bool не принимается вместо числа."""
        with self.assertRaises(TypeError):
            craft(mass_kg=True)

    def test_tc_09_nan_not_valid(self):
        """TC-09: Не допускается nan."""
        with self.assertRaises(ValueError):
            craft(mass_kg=math.nan)

    def test_tc_10_read_only_properties(self):
        """TC-10: Публичные атрибуты неизменяемы прямым присваиванием."""
        obj = craft()
        with self.assertRaises(AttributeError):
            obj.energy = 12
        self.assertEqual(obj.energy, 100)

    def test_tc_11_cruise_energy_is_pure(self):
        """TC-11: Стоимость обычного хода = 2 единицы/км."""
        obj = craft()
        before = obj.get_status()
        actual = obj.calculate_energy(5, "cruise")
        self.assertEqual(actual, 10)
        self.assertEqual(obj.get_status(), before)

    def test_tc_12_boost_energy_is_pure(self):
        """TC-12: Стоимость ускоренного хода = 4 единицы/км."""
        obj = craft()
        self.assertEqual(obj.calculate_energy(5, "boost"), 20)

    def test_tc_13_no_surcharge_at_100(self):
        """TC-13: Ровно 100 м не является глубоководным ходом."""
        obj = craft()
        obj.dive(100)
        self.assertEqual(obj.calculate_energy(5), 10)

    def test_tc_14_surcharge_over_100(self):
        """TC-14: Надбавка 1 ед/км действует глубже 100 м."""
        obj = craft()
        obj.dive(101)
        self.assertEqual(obj.calculate_energy(5), 15)

    def test_tc_15_cruise_movement(self):
        """TC-15: Успешный круиз изменяет позицию и энергию."""
        obj = craft()
        actual = obj.move(10, "cruise")
        self.assertAlmostEqual(actual, 0.25)
        self.assertEqual(obj.position_km, 10)
        self.assertEqual(obj.energy, 80)

    def test_tc_16_boost_movement(self):
        """TC-16: Ускорение увеличивает скорость в 1.5 раза."""
        obj = craft()
        actual = obj.move(5, "boost")
        self.assertAlmostEqual(actual, 1 / 12)
        self.assertEqual(obj.energy, 80)

    def test_tc_17_exact_energy_spend(self):
        """TC-17: Ровно доступная энергия может быть потрачена."""
        obj = craft()
        obj.move(50)
        self.assertEqual(obj.energy, 0)
        self.assertEqual(obj.position_km, 50)

    def test_tc_18_dive_cost(self):
        """TC-18: Погружение на 20 м расходует 2 ед."""
        obj = craft()
        cost = obj.dive(20)
        self.assertEqual(cost, 2)
        self.assertEqual(obj.depth_m, 20)
        self.assertEqual(obj.energy, 98)
        self.assertTrue(obj.is_submerged)

    def test_tc_19_too_deep_atomic(self):
        """TC-19: Избыточная глубина вызывает доменное исключение без изменений."""
        obj = craft()
        before = obj.get_status()
        with self.assertRaises(PodkotiniTooDeep):
            obj.dive(201)
        self.assertEqual(obj.get_status(), before)

    def test_tc_20_dive_not_enough_energy(self):
        """TC-20: Недостаточно энергии для погружения."""
        obj = craft(energy=1)
        before = obj.get_status()
        with self.assertRaises(PodkotiniNoEnergy):
            obj.dive(20)
        self.assertEqual(obj.get_status(), before)

    def test_tc_21_surface_cost(self):
        """TC-21: Всплытие с 20 м требует 1 ед энергии."""
        obj = craft()
        obj.dive(20)
        cost = obj.surface()
        self.assertEqual(cost, 1)
        self.assertEqual(obj.energy, 97)
        self.assertEqual(obj.depth_m, 0)
        self.assertFalse(obj.is_submerged)

    def test_tc_22_surface_noop_at_zero_with_zero_hull(self):
        """TC-22: Всплытие на поверхности — no-op даже при 0% корпуса."""
        obj = craft(hull_integrity=0)
        before = obj.get_status()
        self.assertEqual(obj.surface(), 0)
        self.assertEqual(obj.get_status(), before)

    def test_tc_23_reef_at_20(self):
        """TC-23: Риф проходим начиная с 20 м."""
        obj = craft()
        obj.dive(20)
        before = obj.get_status()
        self.assertTrue(obj.can_overcome("reef"))
        self.assertEqual(obj.get_status(), before)

    def test_tc_24_current_under_30(self):
        """TC-24: При энергии ниже 30 течение непроходимо."""
        obj = craft(energy=29)
        self.assertFalse(obj.can_overcome("current"))

    def test_tc_25_narrow_passage(self):
        """TC-25: Плавник 1.8 м проходит узкий проход."""
        obj = craft()
        self.assertTrue(obj.can_overcome("narrow_passage"))

    def test_tc_26_surface_net(self):
        """TC-26: Сеть непроходима на поверхности."""
        obj = craft()
        self.assertFalse(obj.can_overcome("surface_net"))

    def test_tc_27_recharge_cap(self):
        """TC-27: Заряд ограничен 100."""
        obj = craft(energy=80)
        self.assertIsNone(obj.recharge(1000))
        self.assertEqual(obj.energy, 100)

    def test_tc_28_damage_floor(self):
        """TC-28: Целостность не уходит ниже нуля."""
        obj = craft()
        self.assertIsNone(obj.damage(120))
        self.assertEqual(obj.hull_integrity, 0)

    def test_tc_29_repair_cap(self):
        """TC-29: Ремонт не поднимает целостность выше 100."""
        obj = craft(hull_integrity=10)
        self.assertIsNone(obj.repair(500))
        self.assertEqual(obj.hull_integrity, 100)

    def test_tc_30_immobilized_movement_atomic(self):
        """TC-30: Разрушенный транспорт не двигается."""
        obj = craft(hull_integrity=0)
        before = obj.get_status()
        with self.assertRaises(PodkotiniImmobilized):
            obj.move(1)
        self.assertEqual(obj.get_status(), before)

    def test_tc_31_exact_status_keys(self):
        """TC-31: Статус содержит только оговоренные поля."""
        obj = craft()
        self.assertEqual(set(obj.get_status()), {
            "name", "energy", "hull_integrity", "position_km", "depth_m",
            "is_submerged", "tail_span_m",
        })

    def test_tc_32_status_is_copy(self):
        """TC-32: Изменение снимка не меняет объект."""
        obj = craft()
        status = obj.get_status()
        status["energy"] = -100
        self.assertEqual(obj.energy, 100)
