import pathlib
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# Find the Excel file
file_path = pathlib.Path("clean_data", "capex_capacity.xlsx")

# Load the spreadsheet into a table
df = pd.read_excel(file_path)

# --- Step 1: convert capacity from scfm to m3/h ---
# Keep the original reported capacity and units.
# Create a new column for the converted capacity.

SCFM_TO_M3H = 1.699

df["capacity_m3_per_hr"] = df["reported_capacity"].astype(float)

is_scfm = df["reported_capacity_units"].str.lower() == "scfm"

df.loc[is_scfm, "capacity_m3_per_hr"] = (
    df.loc[is_scfm, "reported_capacity"] * SCFM_TO_M3H
)

# --- Step 2: convert "price per unit" capex rows into a total EUR price ---
# total EUR = price per unit x capacity

per_unit_prices = ["eur_per_nm3_per_hr", "eur_per_m3_per_hr"]

df["reported_capex"] = df["reported_capex"].astype(float)

is_per_unit = df["reported_capex_units"].str.lower().isin(per_unit_prices)

df.loc[is_per_unit, "reported_capex"] = (
    df.loc[is_per_unit, "reported_capex"]
    * df.loc[is_per_unit, "capacity_m3_per_hr"]
)

df.loc[is_per_unit, "reported_capex_units"] = "EUR"

# --- Step 3: add a USD column, using each row's year's exchange rate ---

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

# Start by copying reported_capex as-is
df["reported_capex_usd"] = df["reported_capex"].astype(float)

# For EUR rows, multiply by that year's exchange rate
is_eur = df["reported_capex_units"] == "EUR"

df.loc[is_eur, "reported_capex_usd"] = (
    df.loc[is_eur, "reported_capex"]
    * df.loc[is_eur, "year"].map(eur_to_usd_rate)
)

# --- Step 4: adjust capex for inflation to 2025 dollars using CEPCI ---

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

cepci_ratio = cepci[2025] / df["year"].map(cepci)

df["reported_capex_usd_2025"] = (
    df["reported_capex_usd"] * cepci_ratio
)

# --- Step 5: new columns for the six main upgrading technologies ---
# Rows that are NOT one of these six are left blank in the new columns.

# Remove extra spaces from technology names
df["technology"] = df["technology"].str.strip()

main_technologies = [
    "Water scrubbing",
    "Pressure swing adsorption",
    "Membrane separation",
    "Amine scrubbing",
    "Physical absorption (organic solvent)",
    "Water scrubbing + PSA (O2/N2 removal)",
]

is_main = df["technology"].isin(main_technologies)

# --- Step 6: take out the unreliable membrane values ---
# The Hagen et al. 2001 membrane rows give capex values that are either
# far too high (about 48 to 167 million USD) or far too low (below
# 150,000 USD) compared with every other source, so they are left out.

is_bad_membrane = (
    (df["technology"] == "Membrane separation")
    & (df["source"].str.strip() == "Hagen et al. 2001")
)

keep = is_main & ~is_bad_membrane

# The technology name (only for the rows we keep)
df["main_technology"] = df["technology"].where(keep)

# Their capex in 2025 USD (only for the rows we keep)
df["main_technology_capex_usd_2025"] = df["reported_capex_usd_2025"].where(keep)

print(f"Rows kept for the plot: {keep.sum()}")
print(f"Membrane rows taken out: {(is_main & is_bad_membrane).sum()}")

# --- Save the result back into the same file ---

df.to_excel(file_path, index=False)

print(
    f"Done! Updated {file_path} with "
    "capacity_m3_per_hr, reported_capex_usd, "
    "reported_capex_usd_2025, main_technology, "
    "and main_technology_capex_usd_2025"
)

# --- Step 7: plot capex (2025 USD) vs capacity for the filtered data ---

plot_path = Path("clean_data","capex_vs_capacity.png")
plot_path.parent.mkdir(parents=True, exist_ok=True)

plot_df = df.dropna(subset=["main_technology"])

# Colors for the different technologies
high_contrast_colors = [
    "#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4", "#42d4f4",
]

color_for = dict(zip(main_technologies, high_contrast_colors))

# Larger text everywhere
plt.rcParams.update({"font.size": 14})

fig, ax = plt.subplots(figsize=(10, 6))

# Plot each technology, with a dark outline around each point
for technology in main_technologies:
    group = plot_df[plot_df["main_technology"] == technology]
    ax.scatter(
        group["capacity_m3_per_hr"],
        group["main_technology_capex_usd_2025"],
        label=technology,
        color=color_for[technology],
        edgecolor="#333333",
        linewidth=1,
        s=80,
        alpha=0.85,
    )

ax.set_xlabel("Capacity (m³/h)", fontsize=16)
ax.set_ylabel("Capex, inflation-adjusted to 2025 (USD)", fontsize=16)
ax.set_title("Capex vs Capacity", fontsize=18)

ax.set_xlim(left=0)
ax.set_ylim(bottom=0)

# Tick labels like 1,000 and 4M
ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:,.0f}"))
ax.yaxis.set_major_formatter(
    FuncFormatter(lambda value, _: "0" if value == 0 else f"{value / 1e6:g}M")
)

# No grid; only keep the left and bottom axis lines, ticks pointing inward
ax.grid(False)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_linewidth(1.5)
ax.spines["bottom"].set_linewidth(1.5)
ax.tick_params(direction="in", length=5, width=1.2)

# Put legend below the plot, without a box
ax.legend(
    fontsize=13,
    loc="upper center",
    bbox_to_anchor=(0.5, -0.1),
    ncol=3,
    frameon=False,
)

fig.tight_layout()
fig.savefig(plot_path, dpi=150, bbox_inches="tight")

print(f"Plot saved to {plot_path}")