import pandas as pd
import os
import re
import time

# === Load data ===
print("Loading data...")
master_df = pd.read_csv("public/data_files/1790-2010_MASTER.csv")
data2020_df = pd.read_csv("public/data_files/us2021census.csv")

# === Normalize columns for matching ===
print("Normalizing columns...")
master_df['City'] = master_df['City'].str.strip().str.title()
master_df['ST'] = master_df['ST'].str.strip().str.upper()
master_df['County'] = master_df['County'].str.strip().str.title()

data2020_df['City'] = data2020_df['City'].str.strip().str.title()
data2020_df['State'] = data2020_df['State'].str.strip().str.upper()
data2020_df['Counties'] = data2020_df['Counties'].fillna("").str.strip().str.title()

# === Normalize city columns for matching ===
def normalize_city(city):
    city = city.replace("-", " ").replace("–", " ").replace("—", " ")
    city = city.strip().lower()
    # Replace saint/st/st. at start or after space with 'st'
    city = re.sub(r'(^|\s)(saint|st\.?|st)(?=\s)', r'\1st', city)
    city = re.sub(r'\s+city$', '', city)
    city = re.sub(r'\s+', ' ', city)
    return city.strip()

# Precompute the city names for parallel matching
print("Precomputing normalized city columns...")
master_df['NormCity'] = master_df['City'].apply(normalize_city)
data2020_df['NormCity'] = data2020_df['City'].apply(normalize_city)

# For conflict detection, precompute normalized city in city_state_counts
city_state_counts = master_df.groupby(['NormCity', 'ST']).size().reset_index(name='count')

# === Merge 2020 population into master ===
print("Merging 2020 population into master...")
master_df['2020'] = None

# Precompute 2020 city/state counts for conflict detection
data2020_city_state_counts = data2020_df.groupby(['NormCity', 'State']).size().reset_index(name='count')

total = len(master_df)
for idx, row in master_df.iterrows():
    if idx % 1000 == 0:
        print(f"Processing master row {idx+1}/{total}...")
    norm_city = row.NormCity
    state = row.ST
    county = str(row.County).lower() if pd.notna(row.County) else ""

    # Check for conflict in master
    master_conflict = city_state_counts[
        (city_state_counts['ST'] == state) &
        (city_state_counts['NormCity'] == norm_city)
    ]['count'].iloc[0] > 1

    # Check for conflict in 2020 data
    data2020_conflict_rows = data2020_city_state_counts[
        (data2020_city_state_counts['State'] == state) &
        (data2020_city_state_counts['NormCity'] == norm_city)
    ]
    if not data2020_conflict_rows.empty:
        data2020_conflict = data2020_conflict_rows['count'].iloc[0] > 1
    else:
        data2020_conflict = False

    # Find matches in 2020 data (by normalized city/state)
    matches = data2020_df[
        (data2020_df['State'] == state) &
        (data2020_df['NormCity'] == norm_city)
    ]
    # If either dataset has a conflict, require county match
    if (master_conflict or data2020_conflict) and len(matches) > 0:
        county_match_found = False
        for _, match_row in matches.iterrows():
            # Check if master county name appears in the 2020 Counties field
            if county and county in match_row['Counties'].lower():
                master_df.at[idx, '2020'] = match_row['Population']
                print(f"Matched {row.City}, {state} by county ({county}).")
                county_match_found = True
                break
            
        if not county_match_found:
            print(f"No county match for {row.City}, {state} (county: {county}).")
    elif len(matches) == 1:
        master_df.at[idx, '2020'] = matches.iloc[0]['Population']
        print(f"Matched {row.City}, {state} by city/state.")
    elif len(matches) == 0:
        print(f"No match for {row.City}, {state}.")
    else:
        print(f"Ambiguous match for {row.City}, {state} (multiple candidates, no conflict detected).")

# === Add new rows from 2021 data if not present in master ===
print("Checking for new cities in 2021 data...")
new_rows = []
total_2021 = len(data2020_df)
for idx, row in data2020_df.iterrows():
    if idx % 1000 == 0:
        print(f"Processing 2021 row {idx+1}/{total_2021}...")
    norm_city = row.NormCity
    state = row.State

    possible = master_df[
        (master_df['ST'] == state) &
        (master_df['NormCity'] == norm_city)
    ]

    if len(possible) > 1:
        found = False
        for _, mrow in possible.iterrows():
            if pd.isna(mrow['County']):
                continue
            if row.Counties.lower().find(str(mrow['County']).lower()) != -1:
                found = True
                break
    else:
        found = len(possible) > 0

    if not found and row.Population > 2500:
        new_entry = {
            'City': row.City,
            'ST': row.State,
            'County': row.Counties,
            '2020': row.Population,
            'LAT_BING': getattr(row, 'Latitude', None),
            'LON_BING': getattr(row, 'Longitude', None),
        }
        for col in master_df.columns:
            if col.isdigit():
                new_entry[col] = None
        new_entry['2020'] = row.Population
        new_rows.append(new_entry)
        print(f"Adding new city: {row.City}, {state} (Population: {row.Population})")

print(f"Total new cities added: {len(new_rows)}")
if new_rows:
    master_df = pd.concat([master_df, pd.DataFrame(new_rows)], ignore_index=True)

# === Build final dataset with consistent columns ===
print("Building final dataset...")
year_cols = [col for col in master_df.columns if col.isdigit()]
final_df = master_df[['City', 'ST'] + year_cols + ['LAT_BING', 'LON_BING']].copy()
final_df.rename(columns={'ST': 'State', 'LAT_BING': 'Latitude', 'LON_BING': 'Longitude'}, inplace=True)

# === Save result ===
print("Saving merged dataset...")
os.makedirs("public/data_files", exist_ok=True)
output_path = os.path.join("public/data_files", "us_city_populations_1790-2020.csv")
final_df.to_csv(output_path, index=False)

print(f"Merged dataset saved to {output_path}")