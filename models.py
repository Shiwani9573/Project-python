# models.py  (Unit 2: classes, inheritance)

class Appliance:
    """Parent class"""
    def __init__(self, name, watts, hours):
        self.name = name
        self.watts = watts
        self.hours = hours

    def monthly_units(self, days=30):
        return self.watts * self.hours * days / 1000


class AC(Appliance):
    def __init__(self, hours, watts=1500):
        super().__init__("AC", watts, hours)


class Fan(Appliance):
    def __init__(self, hours, watts=75):
        super().__init__("Fan", watts, hours)


class Fridge(Appliance):
    def __init__(self, hours=24, watts=150):
        super().__init__("Fridge", watts, hours)


class TV(Appliance):
    def __init__(self, hours, watts=100):
        super().__init__("TV", watts, hours)


class Geyser(Appliance):
    def __init__(self, hours, watts=2000):
        super().__init__("Geyser", watts, hours)


# Dropdown ke liye default watts (dictionary)
PRESETS = {
    "AC": 1500, "Fan": 75, "Fridge": 150, "TV": 100,
    "Geyser": 2000, "Light": 40, "Washing Machine": 500,
}

CLASS_MAP = {"AC": AC, "Fan": Fan, "Fridge": Fridge, "TV": TV, "Geyser": Geyser}


def make_appliance(name, watts, hours):
    """Known appliance ho to child class, nahi to parent class"""
    cls = CLASS_MAP.get(name)
    if cls:
        return cls(hours, watts)
    return Appliance(name, watts, hours)


# Test (sirf is file ko chalane par chalega)
if __name__ == "__main__":
    items = [AC(8), Fan(12), Fridge()]
    for a in items:
        print(a.name, "->", a.monthly_units(), "units")