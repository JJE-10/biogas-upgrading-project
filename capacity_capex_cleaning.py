from pathlib import Path
import pandas as pd

# Define the file path
file_path = Path("raw_data") / "cost_data_collection.xlsx"

# Read the Capex sheet
df = pd.read_excel(file_path,sheet_name="Capex")

# Select CAPEX and capacity
capex_capacity = df[
    [
        "technology",
        "reported_capex",
        "reported_capex_units",
        "reported_capacity",
        "reported_capacity_units"
    ]
]

# Remove rows where both CAPEX and capacity are missing
capex_capacity = capex_capacity.dropna(subset=["reported_capex", "reported_capacity"],how="any")

# Save to clean_data
capex_capacity.to_excel("raw_data/capex_capacity_cleaned_raw.xlsx",index=False)
