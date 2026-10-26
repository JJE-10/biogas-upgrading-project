import pathlib
import pandas as pd

# Find the Excel file
capex_data_path = pathlib.Path("raw_data", "cost_data_collection.xlsx")

# Read the Capex sheet
df = pd.read_excel(capex_data_path, sheet_name="Capex")

# Get the year from the source
df["year"] = df["source"].str.extract(r"(\d{4})")

# Standardize technology names

# Water scrubbing, except technologies that contain PSA
df.loc[
    df["technology"].str.contains("water scrubbing", case=False, na=False)
    & ~df["technology"].str.contains("PSA", case=False, na=False),
    "technology"
] = "Water scrubbing"

# Membrane technologies
df.loc[
    df["technology"].str.contains("membrane", case=False, na=False),
    "technology"
] = "Membrane separation"

# Chemical absorption
df.loc[
    df["technology"].str.contains("chemical absorption", case=False, na=False),
    "technology"
] = "Amine scrubbing"

# Select the columns we need
capex_capacity = df[
    [
        "technology",
        "reported_capex",
        "reported_capex_units",
        "reported_capacity",
        "reported_capacity_units",
        "source",
        "year"
    ]
]

# Remove rows with missing CAPEX or capacity
capex_capacity = capex_capacity.dropna(
    subset=["reported_capex", "reported_capacity"]
)

# Create the output file path
output_path = pathlib.Path(
    "clean_data",
    "capex_capacity.xlsx"
)

# Save the cleaned data
capex_capacity.to_excel(output_path, index=False)

# Display the data
print(capex_capacity)