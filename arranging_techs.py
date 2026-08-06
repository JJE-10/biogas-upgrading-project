import pandas as pd

# reading excel file
df = pd.read_excel("upgrading_tech.xlsx")

technology_keywords = {
    1: ["psa"],
    2: ["membrane"],
    3: ["biocng"]
}

def sort_order(technology):
    technology = str(technology).lower()
    for order, keywords in technology_keywords.items():
        for keyword in keywords:
            if keyword in technology: 
                return order
            
df["Sort"] = df["Technology"].apply(sort_order)

# Arrange the rows
df = df.sort_values("Sort")

# Remove the temporary column
df = df.drop(columns=["Sort"])

# Save
df.to_excel("Biogas_Technologies_Sorted.xlsx", index=False)

print("Done!")