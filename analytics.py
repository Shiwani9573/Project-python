# analytics.py  (Unit 2: Pandas + NumPy)
import os
import numpy as np
import pandas as pd


def save_appliances(appliances, path="data/usage.csv"):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    rows = [{"name": a.name, "watts": a.watts, "hours": a.hours}
            for a in appliances]
    pd.DataFrame(rows).to_csv(path, index=False)


def load_appliances(path="data/usage.csv"):
    df = pd.read_csv(path)
    # missing hours ko median se fill karna
    df["hours"] = df["hours"].fillna(df["hours"].median()).fillna(0)
    df["units"] = df["watts"] * df["hours"] * 30 / 1000
    return df


def predict_next_bill(past_bills):
    months = np.arange(1, len(past_bills) + 1)
    slope, intercept = np.polyfit(months, past_bills, 1)
    return round(float(slope * (len(past_bills) + 1) + intercept), 2)


# Test (sirf is file ko chalane par chalega)
if __name__ == "__main__":
    from models import AC, Fan, Fridge

    items = [AC(8), Fan(12), Fridge()]
    save_appliances(items, "data/test.csv")
    print(load_appliances("data/test.csv"))

    bills = [2100, 2300, 2600, 2900, 3000, 3200]
    print("Predicted next bill:", predict_next_bill(bills))