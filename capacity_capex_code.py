from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# --- File path ---
file_path = Path("clean_data") / "capex_capacity.xlsx"

# --- Load the spreadsheet into a table ---
df = pd.read_excel(file_path)

# --- Step 1: convert capacity from scfm to m3/h (1 scfm = 1.699 m3/h) ---
SCFM_TO_M3H = 1.699
is_scfm = df["reported_capacity_units"].str.lower() == "scfm"
df.loc[is_scfm, "reported_capacity"] = df.loc[is_scfm, "reported_capacity"] * SCFM_TO_M3H
df.loc[is_scfm, "reported_capacity_units"] = "m3_per_hr"

# --- Step 2: convert "price per unit" capex rows into a total EUR price ---
# total EUR = price per unit x capacity
per_unit_prices = ["eur_per_nm3_per_hr", "eur_per_m3_per_hr"]
is_per_unit = df["reported_capex_units"].str.lower().isin(per_unit_prices)
df.loc[is_per_unit, "reported_capex"] = (
    df.loc[is_per_unit, "reported_capex"] * df.loc[is_per_unit, "reported_capacity"]
)
df.loc[is_per_unit, "reported_capex_units"] = "EUR"

# --- Step 3: add a USD column, using each row's year's exchange rate ---
# Exchange rates: how many USD one EUR was worth, per year
eur_to_usd_rate = {
    2001: 0.8956,
    2006: 1.2556,
    2008: 1.4708,
    2011: 1.3920,
    2012: 1.2848,
    2013: 1.3281,
    2014: 1.3285,
    2015: 1.1095,
    2019: 1.1195,
}

# Start by copying reported_capex as-is (works for USD rows already)
df["reported_capex_usd"] = df["reported_capex"].astype(float)

# For EUR rows only: multiply by that row's year's exchange rate
is_eur = df["reported_capex_units"] == "EUR"
df.loc[is_eur, "reported_capex_usd"] = (
    df.loc[is_eur, "reported_capex"] * df.loc[is_eur, "currency_year"].map(eur_to_usd_rate)
)

# --- Step 4: adjust capex for inflation to 2025 dollars, using CEPCI ---
# CEPCI = Chemical Engineering Plant Cost Index (higher = more expensive to build)
# 2025 cost = original cost x (2025 index / original year's index)
cepci = {
    2001: 394.3,
    2006: 499.6,
    2008: 575.4,
    2011: 585.7,
    2012: 584.6,
    2013: 567.3,
    2014: 576.1,
    2015: 556.8,
    2019: 607.5,
    2025: 812.8,
}

cepci_ratio = cepci[2025] / df["currency_year"].map(cepci)
df["reported_capex_usd_2025"] = df["reported_capex_usd"] * cepci_ratio

# --- Save the result back into the same file ---
df.to_excel(file_path, index=False)

print(f"Done! Updated {file_path} with reported_capex_usd and reported_capex_usd_2025")

# --- Step 5: plot capex (2025 USD) vs capacity ---
plot_path = Path("clean_data") / "capex_vs_capacity.png"
plot_path.parent.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(8, 6))

# one color per technology, so patterns by technology are easy to see
for technology, group in df.groupby("technology"):
    ax.scatter(group["reported_capacity"], group["reported_capex_usd_2025"], label=technology, alpha=0.7)

ax.set_xlabel("Reported capacity (Nm3/hr or m3/hr)")
ax.set_ylabel("Capex, inflation-adjusted to 2025 (USD)")
ax.set_title("Capex vs Capacity")
ax.grid(True, alpha=0.3)
ax.legend(fontsize=7, loc="upper left", bbox_to_anchor=(1, 1))
fig.tight_layout()
fig.savefig(plot_path, dpi=150)

print(f"Plot saved to {plot_path}")