"""Тестовая обёртка-пилот: не входит в публичный API транспорта."""
class Pilot:
    def __init__(self, craft):
        self.craft = craft

    def dive(self, depth):
        return self.craft.dive(depth)

    def surface(self):
        return self.craft.surface()

    def swim(self, distance, mode="cruise"):
        return self.craft.move(distance, mode)

    def charge(self, energy):
        return self.craft.recharge(energy)

    def crash(self, amount):
        return self.craft.damage(amount)

    def fix(self, amount):
        return self.craft.repair(amount)

    def can_pass(self, obstacle):
        return self.craft.can_overcome(obstacle)
