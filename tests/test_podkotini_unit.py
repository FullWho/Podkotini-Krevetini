"""Авторские модульные тесты (AAA). ID соответствует TEST_CASES.md."""
import math
import unittest

from podkotini_krevetini import (
    PodkotiniKrevetini,
    PodkotiniError,
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
        for invalid in (math.inf, -math.inf, 10**400):
            with self.subTest(value=str(invalid)[:24]):
                with self.assertRaises(ValueError):
                    craft(mass_kg=invalid)
        self.assertEqual(craft(name="  Креветини  ").name, "Креветини")

    def test_tc_10_read_only_properties(self):
        """TC-10: Публичные атрибуты неизменяемы прямым присваиванием."""
        obj = craft()
        with self.assertRaises(AttributeError):
            obj.energy = 12
        self.assertEqual(obj.energy, 100)
        for attr in ("name", "mass_kg", "tail_span_m", "max_speed_kmh",
                     "max_depth_m", "energy", "hull_integrity", "position_km",
                     "depth_m", "is_submerged"):
            with self.subTest(attribute=attr):
                value = getattr(obj, attr)
                with self.assertRaises(AttributeError):
                    setattr(obj, attr, value)
                self.assertEqual(getattr(obj, attr), value)

    def test_tc_11_cruise_energy_is_pure(self):
        """TC-11: Стоимость обычного хода = 2 единицы/км."""
        obj = craft()
        before = obj.get_status()
        actual = obj.calculate_energy(5, "cruise")
        self.assertEqual(actual, 10)
        self.assertEqual(obj.get_status(), before)
        for dist, mode, exc in ((0, "cruise", ValueError), (-2, "cruise", ValueError),
                                (1, "Boost", ValueError), (1, "turbo", ValueError),
                                ("5", "cruise", TypeError), (1, 123, TypeError),
                                (math.nan, "cruise", ValueError),
                                (math.inf, "cruise", ValueError),
                                (10**400, "cruise", ValueError),
                                (1e308, "boost", ValueError)):
            with self.subTest(distance=str(dist)[:24], mode=mode):
                with self.assertRaises(exc):
                    obj.calculate_energy(dist, mode)
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
        self.assertAlmostEqual(obj.calculate_energy(1.1, "cruise"), 3.3)

    def test_tc_15_cruise_movement(self):
        """TC-15: Успешный круиз изменяет позицию и энергию."""
        obj = craft()
        actual = obj.move(10, "cruise")
        self.assertAlmostEqual(actual, 0.25)
        self.assertEqual(obj.position_km, 10)
        self.assertEqual(obj.energy, 80)
        for d, mode, exc in ((0, "cruise", ValueError), (-5, "cruise", ValueError),
                             (1, "Boost", ValueError), (1, "turbo", ValueError),
                             (1, 123, TypeError), ("1", "cruise", TypeError),
                             (math.inf, "cruise", ValueError)):
            with self.subTest(distance=d, mode=mode):
                before = obj.get_status()
                with self.assertRaises(exc):
                    obj.move(d, mode)
                self.assertEqual(obj.get_status(), before)
        huge = craft(max_speed_kmh=1.5e308)
        before = huge.get_status()
        with self.assertRaises(ValueError):
            huge.move(1, "boost")
        self.assertEqual(huge.get_status(), before)

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
        obj = craft(energy=0, hull_integrity=0)
        before = obj.get_status()
        with self.assertRaises(PodkotiniImmobilized):
            obj.move(1)
        self.assertEqual(obj.get_status(), before)

    def test_tc_18_dive_cost(self):
        """TC-18: Погружение на 20 м расходует 2 ед."""
        obj = craft()
        cost = obj.dive(20)
        self.assertEqual(cost, 2)
        self.assertEqual(obj.depth_m, 20)
        self.assertEqual(obj.energy, 98)
        self.assertTrue(obj.is_submerged)
        exact = craft(energy=2)
        self.assertAlmostEqual(exact.dive(20), 2)
        self.assertEqual(exact.energy, 0)
        for val in (-1, math.nan, math.inf, "20", True, 10**400):
            probe = craft()
            state = probe.get_status()
            exc = TypeError if isinstance(val, (str, bool)) else ValueError
            with self.subTest(depth=str(val)[:24]):
                with self.assertRaises(exc):
                    probe.dive(val)
                self.assertEqual(probe.get_status(), state)

    def test_tc_19_too_deep_atomic(self):
        """TC-19: Избыточная глубина вызывает доменное исключение без изменений."""
        obj = craft()
        before = obj.get_status()
        with self.assertRaises(PodkotiniTooDeep):
            obj.dive(201)
        self.assertEqual(obj.get_status(), before)
        broken = craft(hull_integrity=0)
        before = broken.get_status()
        with self.assertRaises(PodkotiniTooDeep):
            broken.dive(201)
        self.assertEqual(broken.get_status(), before)
        limit = craft()
        self.assertAlmostEqual(limit.dive(200), 20)
        self.assertEqual(limit.depth_m, 200)

    def test_tc_20_dive_not_enough_energy(self):
        """TC-20: Недостаточно энергии для погружения."""
        obj = craft(energy=1)
        before = obj.get_status()
        with self.assertRaises(PodkotiniNoEnergy):
            obj.dive(20)
        self.assertEqual(obj.get_status(), before)
        broken = craft(hull_integrity=0)
        before = broken.get_status()
        with self.assertRaises(PodkotiniImmobilized):
            broken.dive(20)
        self.assertEqual(broken.get_status(), before)
        reverse = craft()
        reverse.dive(50)
        self.assertAlmostEqual(reverse.dive(20), 3)
        before = reverse.get_status()
        self.assertEqual(reverse.dive(20), 0)
        self.assertEqual(reverse.get_status(), before)
        self.assertAlmostEqual(reverse.dive(0), 2)

    def test_tc_21_surface_cost(self):
        """TC-21: Всплытие с 20 м требует 1 ед энергии."""
        obj = craft()
        obj.dive(20)
        cost = obj.surface()
        self.assertEqual(cost, 1)
        self.assertEqual(obj.energy, 97)
        self.assertEqual(obj.depth_m, 0)
        self.assertFalse(obj.is_submerged)
        exact = craft(energy=3)
        exact.dive(20)
        self.assertAlmostEqual(exact.surface(), 1)
        self.assertEqual(exact.energy, 0)
        no_energy = craft(energy=2)
        no_energy.dive(20)
        state = no_energy.get_status()
        with self.assertRaises(PodkotiniNoEnergy):
            no_energy.surface()
        self.assertEqual(no_energy.get_status(), state)

    def test_tc_22_surface_noop_at_zero_with_zero_hull(self):
        """TC-22: Всплытие на поверхности — no-op даже при 0% корпуса."""
        obj = craft(hull_integrity=0)
        before = obj.get_status()
        self.assertEqual(obj.surface(), 0)
        self.assertEqual(obj.get_status(), before)
        broken = craft()
        broken.dive(20)
        broken.damage(100)
        state = broken.get_status()
        with self.assertRaises(PodkotiniImmobilized):
            broken.surface()
        self.assertEqual(broken.get_status(), state)
        stuck = craft(hull_integrity=0)
        with self.assertRaises(PodkotiniImmobilized):
            stuck.dive(0)

    def test_tc_23_reef_at_20(self):
        """TC-23: Риф проходим начиная с 20 м."""
        obj = craft()
        obj.dive(20)
        before = obj.get_status()
        self.assertTrue(obj.can_overcome("reef"))
        self.assertEqual(obj.get_status(), before)
        obj2 = craft()
        obj2.dive(19.9)
        self.assertFalse(obj2.can_overcome("reef"))
        for invalid, exception in (("iceberg", ValueError), ("Reef", ValueError),
                                   (123, TypeError)):
            with self.subTest(obstacle=invalid):
                state = obj.get_status()
                with self.assertRaises(exception):
                    obj.can_overcome(invalid)
                self.assertEqual(obj.get_status(), state)

    def test_tc_24_current_under_30(self):
        """TC-24: При энергии ниже 30 течение непроходимо."""
        obj = craft(energy=29)
        self.assertFalse(obj.can_overcome("current"))
        self.assertTrue(craft(energy=30).can_overcome("current"))

    def test_tc_25_narrow_passage(self):
        """TC-25: Плавник 1.8 м проходит узкий проход."""
        obj = craft()
        self.assertTrue(obj.can_overcome("narrow_passage"))
        self.assertTrue(craft(tail_span_m=2).can_overcome("narrow_passage"))
        self.assertFalse(craft(tail_span_m=2.01).can_overcome("narrow_passage"))

    def test_tc_26_surface_net(self):
        """TC-26: Сеть непроходима на поверхности."""
        obj = craft()
        self.assertFalse(obj.can_overcome("surface_net"))
        submerged = craft()
        submerged.dive(9.9)
        self.assertFalse(submerged.can_overcome("surface_net"))
        submerged.dive(10)
        self.assertTrue(submerged.can_overcome("surface_net"))
        broken = craft(hull_integrity=0)
        for obstacle in ("reef", "current", "narrow_passage", "surface_net"):
            with self.subTest(obstacle=obstacle):
                self.assertFalse(broken.can_overcome(obstacle))

    def test_tc_27_recharge_cap(self):
        """TC-27: Заряд ограничен 100."""
        obj = craft(energy=80)
        self.assertIsNone(obj.recharge(1000))
        self.assertEqual(obj.energy, 100)
        for invalid, exc in ((0, ValueError), (-1, ValueError),
                             (math.inf, ValueError), (math.nan, ValueError),
                             ("2", TypeError), (True, TypeError),
                             (10**400, ValueError)):
            probe = craft(energy=50)
            before = probe.get_status()
            with self.subTest(value=str(invalid)[:24]):
                with self.assertRaises(exc):
                    probe.recharge(invalid)
                self.assertEqual(probe.get_status(), before)

    def test_tc_28_damage_floor(self):
        """TC-28: Целостность не уходит ниже нуля."""
        obj = craft()
        self.assertIsNone(obj.damage(120))
        self.assertEqual(obj.hull_integrity, 0)
        for invalid, exc in ((0, ValueError), (-1, ValueError),
                             (math.inf, ValueError), ("2", TypeError)):
            probe = craft()
            before = probe.get_status()
            with self.subTest(value=invalid):
                with self.assertRaises(exc):
                    probe.damage(invalid)
                self.assertEqual(probe.get_status(), before)

    def test_tc_29_repair_cap(self):
        """TC-29: Ремонт не поднимает целостность выше 100."""
        obj = craft(hull_integrity=10)
        self.assertIsNone(obj.repair(500))
        self.assertEqual(obj.hull_integrity, 100)
        for invalid, exc in ((0, ValueError), (-1, ValueError),
                             (math.inf, ValueError), ("2", TypeError)):
            probe = craft(hull_integrity=50)
            before = probe.get_status()
            with self.subTest(value=invalid):
                with self.assertRaises(exc):
                    probe.repair(invalid)
                self.assertEqual(probe.get_status(), before)

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
        detail = craft(name="  Креветини  ", energy=45, hull_integrity=35)
        self.assertEqual(detail.get_status(), {
            "name": "Креветини", "energy": 45, "hull_integrity": 35,
            "position_km": 0, "depth_m": 0, "is_submerged": False,
            "tail_span_m": 1.8,
        })

    def test_tc_32_status_is_copy(self):
        """TC-32: Изменение снимка не меняет объект."""
        obj = craft()
        status = obj.get_status()
        status["energy"] = -100
        self.assertEqual(obj.energy, 100)
        self.assertIsNot(obj.get_status(), obj.get_status())
        for exc in (PodkotiniNoEnergy, PodkotiniTooDeep, PodkotiniImmobilized):
            self.assertTrue(issubclass(exc, PodkotiniError))

