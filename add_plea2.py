"""
Rebuild combined dataset with DSPLEA + fixed SAS parser for single-column vars.
"""
import os, re, csv
import pandas as pd

DATA_DIR = "data"

KEY_COLS = [
    "DISTRICT", "OFFGUIDE", "SENTTOT", "SENTIMP",
    "XMINSOR", "XMAXSOR", "NEWRACE", "MONSEX", "AGE",
    "CITIZEN", "NEWEDUC", "CRIMHIST", "CRIMPTS", "WEAPON",
    "DSPLEA", "INOUT", "PRESENT"
]

def parse_sas_positions(sas_path):
    with open(sas_path, 'r') as f:
        text = f.read()
    
    # Find INPUT statement block
    positions = {}
    
    # Match range: VARNAME  start-end
    for m in re.finditer(r'(\b[A-Z]\w+)\s+\$?\s*(\d+)-(\d+)', text):
        name = m.group(1).upper()
        start = int(m.group(2)) - 1
        end = int(m.group(3))
        if name in KEY_COLS:
            positions[name] = (start, end)
    
    # Match single position: VARNAME  pos  (followed by space and next var or newline)
    # These appear in the INPUT statement as e.g. "CRIMHIST  2688"
    # We need context: they appear after ranges, with just a single number
    for m in re.finditer(r'(\b[A-Z]\w+)\s+(\d{3,5})\s', text):
        name = m.group(1).upper()
        pos = int(m.group(2))
        if name in KEY_COLS and name not in positions:
            # Single column vars - width comes from the format section
            # Look for format width: VARNAME  width (single digit after name in format section)
            positions[name] = (pos - 1, pos)  # default 1 char
    
    # Now find widths from format section (e.g. "CRIMHIST 3" means width 3)
    # Format section has: VARNAME  width  (where width is small number like 3, 4, 8)
    format_section = text[text.find('FORMAT'):]  if 'FORMAT' in text else text
    for name in list(positions.keys()):
        start, end = positions[name]
        if end - start == 1:  # single-char default, try to find real width
            # Look for "NAME  width" pattern where width < 20
            pattern = rf'\b{name}\s+(\d{{1,2}})\b'
            for m2 in re.finditer(pattern, text):
                w = int(m2.group(1))
                if 1 <= w <= 12:
                    positions[name] = (start, start + w)
                    break
    
    return positions

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
    
    found = [k for k in KEY_COLS if k in positions]
    print(f"  Found {len(found)}/{len(KEY_COLS)}: {found}")
    
    colspecs = [positions[v] for v in found]
    df = pd.read_fwf(dat_file, colspecs=colspecs, names=found,
                      na_values=['.', ' .', '  .', '   .'])
    df["FISCAL_YEAR"] = int(year_label)
    all_frames.append(df)
    print(f"  → {len(df):,} cases")

# FY2024 from CSV
print("Processing FY2024...")
with open(os.path.join(DATA_DIR, "individual_fy24", "opafy24nid.csv"), 'r') as f:
    reader = csv.reader(f)
    header = next(reader)

target_cols = set(KEY_COLS)
idxs = [i for i, h in enumerate(header) if h in target_cols]
col_names = [header[i] for i in idxs]

with open(os.path.join(DATA_DIR, "individual_fy24", "opafy24nid.csv"), 'r') as f:
    reader = csv.reader(f)
    next(reader)
    rows = [[row[i] for i in idxs] for row in reader]

df24 = pd.DataFrame(rows, columns=col_names)
for c in df24.columns:
    df24[c] = pd.to_numeric(df24[c], errors='coerce')
df24["FISCAL_YEAR"] = 2024
all_frames.append(df24)
print(f"  → {len(df24):,} cases")

combined = pd.concat(all_frames, ignore_index=True)
print(f"\nTotal: {len(combined):,} cases")

for year in sorted(combined["FISCAL_YEAR"].unique()):
    n = len(combined[combined["FISCAL_YEAR"] == year])
    cols_present = combined[combined["FISCAL_YEAR"] == year].dropna(axis=1, how='all').columns
    has_dsplea = "DSPLEA" in cols_present
    has_race = "NEWRACE" in cols_present
    print(f"  {int(year)}: {n:,} cases | DSPLEA: {'✅' if has_dsplea else '❌'} | NEWRACE: {'✅' if has_race else '❌'}")

# DSPLEA distribution
if "DSPLEA" in combined.columns:
    plea_map = {0: "Not Received", 1: "Plea Agreement", 2: "Alt Document",
                3: "Oral Plea", 5: "Straight Plea", 8: "Trial", 9: "Guilty (unknown)"}
    print(f"\nDSPLEA distribution (all years):")
    for code, label in plea_map.items():
        n = (combined["DSPLEA"] == code).sum()
        if n > 0:
            print(f"  {label}: {n:,}")

# Quick analysis: plea vs trial by race
print("\n" + "="*60)
print("PLEA vs TRIAL SENTENCING BY RACE")
print("="*60)
valid = combined[
    (combined["SENTTOT"] >= 0) & (combined["SENTTOT"] < 470) &
    (combined["NEWRACE"].isin([1, 2, 3])) &
    (combined["DSPLEA"].isin([1, 5, 8]))
].copy()
race_map = {1: "White", 2: "Black", 3: "Hispanic"}
valid["Race"] = valid["NEWRACE"].map(race_map)
valid["Plea Type"] = valid["DSPLEA"].map({1: "Plea Deal", 5: "Straight Plea", 8: "Trial"})

for plea_type in ["Plea Deal", "Straight Plea", "Trial"]:
    subset = valid[valid["Plea Type"] == plea_type]
    print(f"\n  {plea_type}:")
    g = subset.groupby("Race")["SENTTOT"].agg(["mean", "median", "count"])
    for race, row in g.iterrows():
        print(f"    {race:12s}  mean={row['mean']:6.1f}mo  median={row['median']:5.1f}mo  n={int(row['count']):,}")

out_path = os.path.join(DATA_DIR, "combined_fy19_fy24.csv")
combined.to_csv(out_path, index=False)
print(f"\n✅ Saved ({os.path.getsize(out_path)/1024/1024:.1f} MB)")
