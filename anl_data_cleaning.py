import pandas as pd
import re

""" Loading WRRFs sheet from the anl_modified excel file """
df = pd.read_excel("anl_modified.xlsx", sheet_name="WRRFs")

def extract_number(value, convert_units=False):
    if pd.isna(value):
        return "N/A"

    text = str(value)
    text_lower = text.lower()

    """Flag non-flow units (e.g. tons/year) as N/A """
    if convert_units and "ton" in text_lower:
        return "N/A"

    # Match numbers with optional comma thousand-separators
    match = re.search(r'-?\d+(?:,\d{3})*(?:\.\d+)?', text)

    if not match:
        return "N/A"

    num_str = match.group().replace(",", "")
    num = float(num_str)

    if convert_units:
        # If "million" appears in the text, the number is already in MGD scale
        # (e.g. "15.7 million gallons/day" means 15.7 MGD) - don't divide again.
        already_millions = "million" in text_lower

        # Catches gal/day, gals/day, gallons/day
        is_raw_gal_per_day = bool(re.search(r'gal(?:lon)?s?\s*/\s*day', text_lower))

        if is_raw_gal_per_day and not already_millions:
            num = num / 1_000_000  # convert raw gallons/day to MGD

    return num

# List the columns you want to process
columns_of_interest = ["Average Amount of Waste ", "Upgraded MMBTU/yr"]

# Specify which columns need gal/day -> MGD conversion
columns_needing_conversion = {"Average Amount of Waste "}

# Build a brand-new, blank DataFrame with just the extracted results
result_df = pd.DataFrame()

for col in columns_of_interest:
    convert = col in columns_needing_conversion
    result_df[col] = df[col].apply(lambda v: extract_number(v, convert_units=convert))

# Save ONLY the extracted columns to a new Excel file
result_df.to_excel("extracted_output.xlsx", index=False)
