
from functools import reduce


SLABS = [
    (100, 4.0),
    (300, 6.0),
    (float("inf"), 7.5),
]


def calculate_bill(units, slabs=SLABS):
    bill = 0
    previous_limit = 0
    for limit, rate in slabs:
        if units > previous_limit:
            slab_units = min(units, limit) - previous_limit
            bill += slab_units * rate
        previous_limit = limit
    return round(bill, 2)


def total_units(appliances):
    return reduce(lambda x, y: x + y,
                  map(lambda a: a.monthly_units(), appliances), 0)


def heavy_appliances(appliances, limit=100):
    return list(filter(lambda a: a.monthly_units() > limit, appliances))


def top_consumer(appliances):
    if not appliances:
        return None
    return max(appliances, key=lambda a: a.monthly_units())


if __name__ == "__main__":
    from models import AC, Fan, Fridge

    items = [AC(8), Fan(12), Fridge()]
    units = total_units(items)
    print("Total units:", units)
    print("Bill: Rs", calculate_bill(units))
    print("Top consumer:", top_consumer(items).name)
    print("Heavy appliances:", [a.name for a in heavy_appliances(items)])