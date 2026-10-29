# charts.py  (Unit 2 Matplotlib, Unit 3 Seaborn + Plotly)
from matplotlib.figure import Figure
import pandas as pd
import seaborn as sns


def pie_fig(appliances):
    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    names = [a.name for a in appliances]
    units = [a.monthly_units() for a in appliances]
    ax.pie(units, labels=names, autopct="%1.1f%%", startangle=90)
    ax.set_title("Appliance-wise Electricity Share")
    ax.legend(names, loc="best", fontsize=8)
    return fig


def bar_fig(bills):
    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    months = [f"M{i}" for i in range(1, len(bills) + 1)]
    ax.bar(months, bills, color="#1f4e9c", label="Bill (Rs)")
    ax.set_title("Monthly Electricity Bill")
    ax.set_xlabel("Month")
    ax.set_ylabel("Bill (Rs)")
    ax.legend()
    return fig


def line_fig(bills, predicted=None):
    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    x = list(range(1, len(bills) + 1))
    ax.plot(x, bills, marker="o", label="Past bills")
    if predicted is not None:
        ax.plot([x[-1], x[-1] + 1], [bills[-1], predicted],
                "--", marker="o", color="red", label="Predicted")
    ax.set_title("Bill Trend and Prediction")
    ax.set_xlabel("Month")
    ax.set_ylabel("Bill (Rs)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    return fig


def heatmap_fig(appliances):
    """Appliance vs daily hours: monthly units"""
    hours_list = [2, 4, 6, 8, 10, 12]
    data = {f"{h} hr": [a.watts * h * 30 / 1000 for a in appliances]
            for h in hours_list}
    df = pd.DataFrame(data, index=[a.name for a in appliances])
    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    sns.heatmap(df, annot=True, fmt=".0f", cmap="YlOrRd", ax=ax)
    ax.set_title("Monthly Units: Appliance vs Daily Hours")
    return fig


def plotly_trend(bills, predicted=None):
    import plotly.graph_objects as go
    x = list(range(1, len(bills) + 1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=bills, mode="lines+markers", name="Past bills"))
    if predicted is not None:
        fig.add_trace(go.Scatter(x=[x[-1], x[-1] + 1], y=[bills[-1], predicted],
                                 mode="lines+markers", name="Predicted",
                                 line=dict(dash="dash", color="red")))
    fig.update_layout(title="Interactive Bill Trend",
                      xaxis_title="Month", yaxis_title="Bill (Rs)")
    fig.show()


# Test (sirf is file ko chalane par chalega)
if __name__ == "__main__":
    from models import AC, Fan, Fridge

    items = [AC(8), Fan(12), Fridge()]
    bills = [2100, 2300, 2600, 2900, 3000, 3200]

    pie_fig(items).savefig("test_pie.png")
    bar_fig(bills).savefig("test_bar.png")
    line_fig(bills, 3473.33).savefig("test_line.png")
    heatmap_fig(items).savefig("test_heatmap.png")
    print("4 images ban gayi: test_pie, test_bar, test_line, test_heatmap")

    plotly_trend(bills, 3473.33)   # browser mein khulega