"""
Extract DSPLEA (plea vs trial) from all years and rebuild combined dataset.
Also attempt to get DEFCONSL (attorney type) from FY1999-2003.
"""
import os
import re
import pandas as pd
import pyreadstat

DATA_DIR = "data"

# Parse SAS positions
def parse_sas_positions(sas_path):
    with open(sas_path, 'r') as f:
        text = f.read()
    positions = {}
    for m in re.finditer(r'(\w+)\s+\$?\s*(\d+)-(\d+)', text):
        positions[m.group(1).upper()] = (int(m.group(2)) - 1, int(m.group(3)))
    return positions

# Extended key columns
KEY_COLS = [
    "DISTRICT", "OFFGUIDE", "SENTTOT", "SENTIMP",
    "XMINSOR", "XMAXSOR", "NEWRACE", "MONSEX", "AGE",
    "CITIZEN", "NEWEDUC", "CRIMHIST", "CRIMPTS", "WEAPON",
    "DSPLEA", "INOUT", "PRESENT"
]

YEARS = {"19": "2019", "20": "2020", "21": "2021", "22": "2022", "23": "2023"}

all_frames = []

for suffix, year_label in sorted(YEARS.items()):
    sas_dir = os.path.join(DATA_DIR, f"sas_fy{suffix}")
    sas_file = os.path.join(sas_dir, f"opafy{suffix}nid.sas")
    dat_file = os.path.join(sas_dir, f"opafy{suffix}nid.dat")
    
    if not os.path.exists(dat_file):
        continue
    
    print(f"Processing FY{year_label}...")
    positions = parse_sas_positions(sas_file)
    available = {v: positions[v] for v in KEY_COLS if v in positions}
    
    colspecs = [(pos[0], pos[1]) for pos in available.values()]
    names = list(available.keys())
    
    df = pd.read_fwf(dat_file, colspecs=colspecs, names=names,
                      na_values=['.', ' .', '  .', '   .'])
    df["FISCAL_YEAR"] = int(year_label)
    all_frames.append(df)
    print(f"  → {len(df):,} cases, cols: {list(available.keys())}")

# FY2024 — need to extract DSPLEA from the big CSV
print("Processing FY2024...")
# Get column positions
import csv
with open(os.path.join(DATA_DIR, "individual_fy24", "opafy24nid.csv"), 'r') as f:
    reader = csv.reader(f)
    header = next(reader)

# Find our columns
target_cols = set(KEY_COLS)
idxs = [i for i, h in enumerate(header) if h in target_cols]
col_names = [header[i] for i in idxs]
print(f"  Found cols: {col_names}")

# Extract
with open(os.path.join(DATA_DIR, "individual_fy24", "opafy24nid.csv"), 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
    rows = []
    for row in reader:
        rows.append([row[i] for i in idxs])

df24 = pd.DataFrame(rows, columns=col_names)
# Convert numeric
for c in df24.columns:
    df24[c] = pd.to_numeric(df24[c], errors='coerce')
df24["FISCAL_YEAR"] = 2024
all_frames.append(df24)
print(f"  → {len(df24):,} cases")

print(f"\nCombining {len(all_frames)} years...")
combined = pd.concat(all_frames, ignore_index=True)
print(f"Total: {len(combined):,} cases")

for year in sorted(combined["FISCAL_YEAR"].unique()):
    n = len(combined[combined["FISCAL_YEAR"] == year])
    print(f"  {int(year)}: {n:,}")

# Check DSPLEA coverage
if "DSPLEA" in combined.columns:
    plea_counts = combined["DSPLEA"].value_counts().sort_index()
    print(f"\nDSPLEA distribution:")
    plea_map = {0: "Not Received", 1: "Plea Agreement", 2: "Alt Document", 
                3: "Oral Plea", 5: "Straight Plea (no deal)", 8: "Trial", 9: "Guilty Plea (unknown type)"}
    for code, count in plea_counts.items():
        label = plea_map.get(int(code), f"Code {int(code)}")
        print(f"  {label}: {count:,}")

out_path = os.path.join(DATA_DIR, "combined_fy19_fy24.csv")
combined.to_csv(out_path, index=False)
print(f"\n✅ Saved to {out_path} ({os.path.getsize(out_path)/1024/1024:.1f} MB)")
