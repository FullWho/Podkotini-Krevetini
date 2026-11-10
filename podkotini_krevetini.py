"""Модель биомеханического подводного транспорта «Подкотини Креветини»."""
import math


class PodkotiniError(Exception):
    """Базовое исключение предметной области."""


class PodkotiniNoEnergy(PodkotiniError):
    """Недостаточно энергии для действия."""


class PodkotiniTooDeep(PodkotiniError):
    """Превышена разрешённая глубина."""


class PodkotiniImmobilized(PodkotiniError):
    """Движитель отключён из-за полного разрушения корпуса."""


def _number(value, name, minimum=None, maximum=None, strict=False):
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise TypeError(f"{name} must be numeric")
    try:
        value = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} must be finite") from exc
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if minimum is not None and (value <= minimum if strict else value < minimum):
        raise ValueError(f"{name} out of range")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} out of range")
    return value


class PodkotiniKrevetini:
    """Водный биомеханический транспорт с герметичной кабиной."""

    def __init__(self, name: str, mass_kg: float, tail_span_m: float,
                 max_speed_kmh: float, max_depth_m: float,
                 energy: float = 100.0, hull_integrity: float = 100.0) -> None:
        if not isinstance(name, str):
            raise TypeError("name must be string")
        if not name.strip():
            raise ValueError("name must not be empty")
        self._name = name.strip()
        self._mass_kg = _number(mass_kg, "mass_kg", 0, strict=True)
        self._tail_span_m = _number(tail_span_m, "tail_span_m", 0, strict=True)
        self._max_speed_kmh = _number(max_speed_kmh, "max_speed_kmh", 0, strict=True)
        self._max_depth_m = _number(max_depth_m, "max_depth_m", 0, strict=True)
        self._energy = _number(energy, "energy", 0, 100)
        self._hull_integrity = _number(hull_integrity, "hull_integrity", 0, 100)
        self._position_km = 0.0
        self._depth_m = 0.0

    @property
    def name(self): return self._name

    @property
    def mass_kg(self): return self._mass_kg

    @property
    def tail_span_m(self): return self._tail_span_m

    @property
    def max_speed_kmh(self): return self._max_speed_kmh

    @property
    def max_depth_m(self): return self._max_depth_m

    @property
    def energy(self): return self._energy

    @property
    def hull_integrity(self): return self._hull_integrity

    @property
    def position_km(self): return self._position_km

    @property
    def depth_m(self): return self._depth_m

    @property
    def is_submerged(self): return self._depth_m > 0

    def calculate_energy(self, distance_km: float, speed_mode: str = "cruise") -> float:
        distance = _number(distance_km, "distance_km", 0, strict=True)
        if not isinstance(speed_mode, str):
            raise TypeError("speed_mode must be string")
        if speed_mode not in ("cruise", "boost"):
            raise ValueError("unknown speed_mode")
        cost = distance * (2 if speed_mode == "cruise" else 4) + (distance if self.depth_m > 100 else 0)
        if not math.isfinite(cost):
            raise ValueError("calculated energy cost must be finite")
        return cost

    def _ensure_working(self):
        if self.hull_integrity == 0:
            raise PodkotiniImmobilized("tail drive disabled: hull integrity is zero")

    def _ensure_energy(self, cost):
        if self.energy < cost:
            raise PodkotiniNoEnergy(f"need {cost} energy, have {self.energy}")

    def move(self, distance_km: float, speed_mode: str = "cruise") -> float:
        cost = self.calculate_energy(distance_km, speed_mode)
        speed = self.max_speed_kmh * (1.5 if speed_mode == "boost" else 1)
        if not math.isfinite(speed) or speed <= 0:
            raise ValueError("calculated speed must be positive and finite")
        time_h = float(distance_km) / speed
        if not math.isfinite(time_h):
            raise ValueError("calculated time must be finite")
        new_position = self.position_km + float(distance_km)
        if not math.isfinite(new_position):
            raise ValueError("position would overflow")
        self._ensure_working()
        self._ensure_energy(cost)
        self._position_km = new_position
        self._energy -= cost
        return time_h

    def dive(self, target_depth_m: float) -> float:
        depth = _number(target_depth_m, "target_depth_m", 0)
        if depth > self.max_depth_m:
            raise PodkotiniTooDeep("target exceeds max depth")
        self._ensure_working()
        cost = abs(depth - self.depth_m) * 0.1
        self._ensure_energy(cost)
        self._depth_m = depth
        self._energy -= cost
        return cost

    def surface(self) -> float:
        if self.depth_m == 0:
            return 0.0
        self._ensure_working()
        cost = self.depth_m * 0.05
        self._ensure_energy(cost)
        self._depth_m = 0.0
        self._energy -= cost
        return cost

    def can_overcome(self, obstacle: str) -> bool:
        if not isinstance(obstacle, str):
            raise TypeError("obstacle must be string")
        conditions = {
            "reef": self.depth_m >= 20,
            "current": self.energy >= 30,
            "narrow_passage": self.tail_span_m <= 2,
            "surface_net": self.depth_m >= 10,
        }
        if obstacle not in conditions:
            raise ValueError("unknown obstacle")
        return self.hull_integrity > 0 and conditions[obstacle]

    def recharge(self, amount: float) -> None:
        value = _number(amount, "amount", 0, strict=True)
        self._energy = min(100.0, self._energy + value)

    def damage(self, amount: float) -> None:
        value = _number(amount, "amount", 0, strict=True)
        self._hull_integrity = max(0.0, self._hull_integrity - value)

    def repair(self, amount: float) -> None:
        value = _number(amount, "amount", 0, strict=True)
        self._hull_integrity = min(100.0, self._hull_integrity + value)

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "energy": self.energy,
            "hull_integrity": self.hull_integrity,
            "position_km": self.position_km,
            "depth_m": self.depth_m,
            "is_submerged": self.is_submerged,
            "tail_span_m": self.tail_span_m,
        }
