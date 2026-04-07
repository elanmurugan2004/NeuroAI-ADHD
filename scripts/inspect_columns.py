import pandas as pd

df = pd.read_csv("data/raw/adhd_phenotypic_40.csv")
print("Shape:", df.shape)
print("\nColumns:")
for c in df.columns:
    print("-", c)
print("\nHead:")
print(df.head())
print("\nMissing values:")
print(df.isnull().sum().sort_values(ascending=False).head(20))