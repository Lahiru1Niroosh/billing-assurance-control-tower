import pandas as pd
from config import RAW, REPORTS

df = pd.read_csv(RAW, dtype=str, keep_default_na=False)
print("Shape:", df.shape)

blank = df.apply(lambda s: s.str.strip().eq("")).sum()
print("\nBlank cells per column:\n", blank[blank > 0])

print("\nDuplicate customerIDs:", df["customerID"].duplicated().sum())
print("Full-row duplicates:", df.duplicated().sum())

tc = pd.to_numeric(df["TotalCharges"], errors="coerce")
bad = df.loc[tc.isna(), ["customerID", "tenure", "MonthlyCharges", "TotalCharges"]]
print("\nNon-numeric TotalCharges rows:\n", bad)

for col in ["Contract", "PaymentMethod", "InternetService", "Churn"]:
    print(f"\n{col}:\n", df[col].value_counts())

REPORTS.mkdir(exist_ok=True)
bad.to_csv(REPORTS / "raw_profile_blank_totalcharges.csv", index=False)