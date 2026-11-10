"""Авторские функциональные тесты (Given/When/Then через тестового пилота)."""
import unittest

from podkotini_krevetini import (
    PodkotiniKrevetini, PodkotiniImmobilized, PodkotiniNoEnergy,
    PodkotiniTooDeep,
)
from tests.pilot import Pilot


def setup(energy=100):
    craft = PodkotiniKrevetini(
        name="Подкотини Креветини", mass_kg=250, tail_span_m=1.8,
        max_speed_kmh=40, max_depth_m=200, energy=energy,
    )
    return craft, Pilot(craft)


class TestPodkotiniScenarios(unittest.TestCase):
    def test_tc_33_coral_labyrinth_end_state(self):
        """TC-33: S1, погружение, круиз, ускорение и подъём."""
        # Given: аппарат на поверхности с полным аккумулятором.
        craft, pilot = setup()
        # When: пилот проходит весь маршрут.
        pilot.dive(20)
        self.assertTrue(pilot.can_pass("reef"))
        pilot.swim(10)
        pilot.swim(5, "boost")
        pilot.surface()
        # Then: конечное состояние совпадает с SPEC 4.2 S1.
        self.assertEqual(craft.position_km, 15)
        self.assertEqual(craft.energy, 57)
        self.assertEqual(craft.depth_m, 0)
        self.assertFalse(craft.is_submerged)

    def test_tc_34_coral_labyrinth_travel_times(self):
        """TC-34: S1, два времени движения соответствуют режимам."""
        # Given
        craft, pilot = setup()
        pilot.dive(20)
        # When
        cruise_time = pilot.swim(10)
        boost_time = pilot.swim(5, "boost")
        # Then
        self.assertAlmostEqual(cruise_time, 0.25)
        self.assertAlmostEqual(boost_time, 1 / 12)

    def test_tc_35_deep_water_route(self):
        """TC-35: S2, глубоководная надбавка и всплытие."""
        # Given
        craft, pilot = setup()
        # When
        pilot.dive(120)
        self.assertEqual(craft.energy, 88)
        pilot.swim(10)
        self.assertEqual(craft.energy, 58)
        before = craft.get_status()
        with self.assertRaises(PodkotiniTooDeep):
            pilot.dive(201)
        self.assertEqual(craft.get_status(), before)
        pilot.surface()
        # Then
        self.assertEqual(craft.energy, 52)
        self.assertEqual(craft.position_km, 10)
        self.assertEqual(craft.depth_m, 0)

    def test_tc_36_deep_water_limit_atomic(self):
        """TC-36: S2, отказ при превышении предела глубины."""
        # Given
        craft, pilot = setup()
        pilot.dive(120)
        before = craft.get_status()
        # When/Then
        with self.assertRaises(PodkotiniTooDeep):
            pilot.dive(201)
        self.assertEqual(craft.get_status(), before)

    def test_tc_37_hull_destroyed_route(self):
        """TC-37: S3, столкновение обездвиживает аппарат."""
        # Given
        craft, pilot = setup()
        # When
        pilot.swim(4)
        pilot.crash(100)
        state = craft.get_status()
        # Then
        with self.assertRaises(PodkotiniImmobilized):
            pilot.swim(1)
        self.assertEqual(craft.get_status(), state)
        self.assertEqual(craft.position_km, 4)

    def test_tc_38_repaired_route(self):
        """TC-38: S3, ремонт возвращает подвижность."""
        # Given
        craft, pilot = setup()
        pilot.swim(4)
        pilot.crash(100)
        # When
        before = craft.get_status()
        with self.assertRaises(PodkotiniImmobilized):
            pilot.swim(1)
        self.assertEqual(craft.get_status(), before)
        pilot.fix(25)
        pilot.swim(1)
        # Then
        self.assertEqual(craft.hull_integrity, 25)
        self.assertEqual(craft.energy, 90)
        self.assertEqual(craft.position_km, 5)

    def test_tc_39_energy_failure_route(self):
        """TC-39: S4, ускорение после погружения не обеспечено энергией."""
        # Given
        craft, pilot = setup(energy=25)
        pilot.dive(100)
        before = craft.get_status()
        # When/Then
        with self.assertRaises(PodkotiniNoEnergy):
            pilot.swim(10, "boost")
        self.assertEqual(craft.get_status(), before)
        self.assertEqual(craft.position_km, 0)

    def test_tc_40_return_and_recharge_route(self):
        """TC-40: S4, подъём, зарядка и движение после сбоя."""
        # Given
        craft, pilot = setup(energy=25)
        pilot.dive(100)
        before = craft.get_status()
        with self.assertRaises(PodkotiniNoEnergy):
            pilot.swim(10, "boost")
        self.assertEqual(craft.get_status(), before)
        # When
        pilot.surface()
        pilot.charge(30)
        pilot.swim(5)
        # Then
        self.assertEqual(craft.energy, 30)
        self.assertEqual(craft.position_km, 5)
        self.assertEqual(craft.depth_m, 0)
