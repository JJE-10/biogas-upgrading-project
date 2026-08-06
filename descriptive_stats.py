import pandas as pd
import matplotlib.pyplot as plt

# Load the extracted data
df = pd.read_excel("extracted_output.xlsx")

# Convert "N/A" text back to actual missing values so pandas can plot the rest
df = df.replace("N/A", pd.NA)
for col in df.columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

waste_col = "Average Amount of Waste "
mmbtu_col = "Upgraded MMBTU/yr"

# ---------- Histograms ----------
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].hist(df[waste_col].dropna(), bins=15, color="steelblue", edgecolor="black")
axes[0].set_title("Histogram: Average Amount of Waste (MGD)")
axes[0].set_xlabel("MGD")
axes[0].set_ylabel("Frequency")

axes[1].hist(df[mmbtu_col].dropna(), bins=15, color="darkorange", edgecolor="black")
axes[1].set_title("Histogram: Upgraded MMBTU/yr")
axes[1].set_xlabel("MMBTU/yr")
axes[1].set_ylabel("Frequency")

plt.tight_layout()
plt.savefig("histograms.png", dpi=150)
plt.close()

# ---------- Scatter plot: Waste (x) vs MMBTU (y) ----------
paired = df[[waste_col, mmbtu_col]].dropna()

plt.figure(figsize=(7, 6))
plt.scatter(paired[waste_col], paired[mmbtu_col], color="seagreen", edgecolor="black")
plt.title("Average Amount of Waste vs Upgraded MMBTU/yr")
plt.xlabel("Average Amount of Waste (MGD)")
plt.ylabel("Upgraded MMBTU/yr")
plt.tight_layout()
plt.savefig("scatter_waste_vs_mmbtu.png", dpi=150)
plt.show() 
plt.close()

# ---------- Scatter plot: MMBTU (x) vs Waste (y) ----------
plt.figure(figsize=(7, 6))
plt.scatter(paired[mmbtu_col], paired[waste_col], color="indianred", edgecolor="black")
plt.title("Upgraded MMBTU/yr vs Average Amount of Waste")
plt.xlabel("Upgraded MMBTU/yr")
plt.ylabel("Average Amount of Waste (MGD)")
plt.tight_layout()
plt.savefig("scatter_mmbtu_vs_waste.png", dpi=150)
plt.show() 
plt.close()

print("Done! Saved: histograms.png, boxplots.png, scatter_waste_vs_mmbtu.png, scatter_mmbtu_vs_waste.png")