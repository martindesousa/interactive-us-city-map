import pandas as pd, requests

URL = "https://api.census.gov/data/2020/dec/pl?get=NAME,P1_001N&for=place:*&in=state:*"
r = requests.get(URL, timeout=60)
r.raise_for_status()

cols, *rows = r.json()
df = pd.DataFrame(rows, columns=cols).rename(
    columns={"NAME":"name","P1_001N":"population_2020","state":"state_fips","place":"place_fips"}
)

# Filter to CDPs (NAME contains "CDP") and population > 10,000
df = df[df["name"].str.contains("CDP")]
df["population_2020"] = pd.to_numeric(df["population_2020"], errors="coerce")
df = df[df["population_2020"] > 25000]

# Add GEOID and tidy/order
df["geoid"] = df["state_fips"] + df["place_fips"]
out = df[["name","state_fips","place_fips","geoid","population_2020"]].sort_values("population_2020", ascending=False)
out.to_csv("cdps_over_25k_2020.csv", index=False)
print(f"Done. Rows: {len(out)}  -> cdps_over_25k_2020.csv")