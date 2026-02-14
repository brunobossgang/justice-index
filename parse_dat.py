"""
Parse USSC .dat fixed-width files using column positions from .sas syntax.
Extract only key columns and save as slim CSV per year.
"""
import os
import re
import pandas as pd

DATA_DIR = "data"

# Column positions extracted from SAS files (0-indexed start, end exclusive)
# Format in SAS: VARNAME  start-end  (1-indexed)
# We parse each year's .sas to get positions

def parse_sas_positions(sas_path):
    """Extract variable name -> (start, end) from SAS INPUT statement only."""
    with open(sas_path, 'r') as f:
        text = f.read()
    
    # Restrict to INPUT section only (avoids FORMAT/INFORMAT confusion)
    input_match = re.search(r'INPUT\s(.*?);', text, re.DOTALL)
    if not input_match:
        raise ValueError(f"No INPUT section found in {sas_path}")
    input_text = input_match.group(1)
    
    positions = {}
    # Range columns: VARNAME  start-end  or  VARNAME $ start-end
    for m in re.finditer(r'(\w+)\s+\$?\s*(\d+)-(\d+)', input_text):
        name = m.group(1).upper()
        start = int(m.group(2)) - 1  # 0-indexed
        end = int(m.group(3))        # SAS end is inclusive → exclusive
        positions[name] = (start, end)
    
    # Single-column: VARNAME  pos  (just a number, no dash)
    for m in re.finditer(r'(\w+)\s+\$?\s*(\d+)(?:\s|$)', input_text):
        name = m.group(1).upper()
        pos = int(m.group(2))
        if name not in positions and pos > 10:  # skip tiny positions that are likely format widths
            positions[name] = (pos - 1, pos)
    
    return positions

KEY_VARS = ["SENTTOT", "NEWRACE", "MONSEX", "AGE", "OFFGUIDE", "DISTRICT",
            "XMINSOR", "XMAXSOR", "CRIMHIST", "CRIMPTS", "CITIZEN", 
            "NEWEDUC", "WEAPON", "SENTIMP", "DSPLEA", "INOUT", "PRESENT"]

YEARS = {
    "19": "2019", "20": "2020", "21": "2021", "22": "2022", "23": "2023"
}

all_frames = []

for suffix, year_label in sorted(YEARS.items()):
    sas_dir = os.path.join(DATA_DIR, f"sas_fy{suffix}")
    sas_file = os.path.join(sas_dir, f"opafy{suffix}nid.sas")
    dat_file = os.path.join(sas_dir, f"opafy{suffix}nid.dat")
    
    if not os.path.exists(dat_file):
        print(f"⚠️  {year_label}: .dat not found, skipping")
        continue
    
    print(f"Processing FY{year_label}...")
    
    # Parse column positions from SAS
    positions = parse_sas_positions(sas_file)
    
    # Check which key vars we have
    available = {v: positions[v] for v in KEY_VARS if v in positions}
    missing = [v for v in KEY_VARS if v not in positions]
    if missing:
        print(f"  Missing vars: {missing}")
    
    print(f"  Found {len(available)}/{len(KEY_VARS)} key variables")
    
    # Build colspecs for pandas
    colspecs = [(pos[0], pos[1]) for pos in available.values()]
    names = list(available.keys())
    
    # Read fixed-width file
    df = pd.read_fwf(dat_file, colspecs=colspecs, names=names, 
                      na_values=['.', ' .', '  .', '   .'])
    
    df["FISCAL_YEAR"] = int(year_label)
    all_frames.append(df)
    print(f"  → {len(df):,} cases")

# Add FY2024 from slim CSV
slim_path = os.path.join(DATA_DIR, "individual_fy24", "slim.csv")
if os.path.exists(slim_path):
    print("Loading FY2024 from slim CSV...")
    df24 = pd.read_csv(slim_path, low_memory=False)
    df24["FISCAL_YEAR"] = 2024
    all_frames.append(df24)
    print(f"  → {len(df24):,} cases")

print(f"\nCombining {len(all_frames)} years...")
combined = pd.concat(all_frames, ignore_index=True)
print(f"Total: {len(combined):,} cases across {combined['FISCAL_YEAR'].nunique()} years")

for year in sorted(combined["FISCAL_YEAR"].unique()):
    n = len(combined[combined["FISCAL_YEAR"] == year])
    print(f"  {int(year)}: {n:,} cases")

out_path = os.path.join(DATA_DIR, "combined_fy19_fy24.csv")
combined.to_csv(out_path, index=False)
print(f"\n✅ Saved to {out_path} ({os.path.getsize(out_path)/1024/1024:.1f} MB)")
