from pathlib import Path
import pandas as pd

# File paths
input_path = Path("raw_data") / "capex_capacity_cleaned_raw.xlsx"
output_path = Path("clean_data") / "capex_capacity.xlsx"

# Load data
df = pd.read_excel(input_path)

# Convert capacity: rows measured in scfm -> m3/h (1 scfm = 1.699 m3/h)
scfm_to_m3h = 1.699
scfm_mask = df["reported_capacity_units"].str.lower() == "scfm"
df.loc[scfm_mask, "reported_capacity"] = df.loc[scfm_mask, "reported_capacity"] * scfm_to_m3h
df.loc[scfm_mask, "reported_capacity_units"] = "m3_per_hr"

# Rows priced per unit (EUR per Nm3/hr or per m3/hr) instead of total EUR
units_to_convert = ["eur_per_nm3_per_hr", "eur_per_m3_per_hr"]
mask = df["reported_capex_units"].str.lower().isin(units_to_convert)

# Convert: total EUR = price per unit x capacity
df.loc[mask, "reported_capex"] = df.loc[mask, "reported_capex"] * df.loc[mask, "reported_capacity"]
df.loc[mask, "reported_capex_units"] = "EUR"

# Save result
output_path.parent.mkdir(parents=True, exist_ok=True)
df.to_excel(output_path, index=False)
