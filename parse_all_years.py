"""Parse ALL USSC years (FY2002-2024) into one combined CSV."""
import os, re, sys
import pandas as pd

DATA_DIR = "data"

KEY_VARS = ["SENTTOT", "NEWRACE", "MONSEX", "AGE", "OFFGUIDE", "DISTRICT",
            "XMINSOR", "XMAXSOR", "CRIMHIST", "CRIMPTS", "CITIZEN",
            "NEWEDUC", "WEAPON", "SENTIMP", "DSPLEA", "INOUT", "PRESENT"]

def parse_sas_positions(sas_path):
    with open(sas_path, 'r', errors='replace') as f:
        text = f.read()
    input_match = re.search(r'INPUT\s(.*?);', text, re.DOTALL)
    if not input_match:
        raise ValueError(f"No INPUT section found in {sas_path}")
    input_text = input_match.group(1)
    positions = {}
    for m in re.finditer(r'(\w+)\s+\$?\s*(\d+)-(\d+)', input_text):
        name = m.group(1).upper()
        start = int(m.group(2)) - 1
        end = int(m.group(3))
        positions[name] = (start, end)
    for m in re.finditer(r'(\w+)\s+\$?\s*(\d+)(?:\s|$)', input_text):
        name = m.group(1).upper()
        pos = int(m.group(2))
        if name not in positions and pos > 10:
            positions[name] = (pos - 1, pos)
    return positions

# All years to process
YEARS = {}
for yr in range(2, 24):
    YEARS[f"{yr:02d}"] = str(2000 + yr)

all_frames = []

for suffix, year_label in sorted(YEARS.items()):
    sas_dir = os.path.join(DATA_DIR, f"sas_fy{suffix}")
    
    # Try different naming patterns
    sas_candidates = [
        os.path.join(sas_dir, f"opafy{suffix}nid.sas"),
        os.path.join(sas_dir, f"opafy{suffix}-nid.sas"),
    ]
    dat_candidates = [
        os.path.join(sas_dir, f"opafy{suffix}nid.dat"),
        os.path.join(sas_dir, f"opafy{suffix}-nid.dat"),
    ]
    
    sas_file = next((f for f in sas_candidates if os.path.exists(f)), None)
    dat_file = next((f for f in dat_candidates if os.path.exists(f)), None)
    
    if not sas_file or not dat_file:
        print(f"⚠️  FY{year_label}: missing sas={sas_file is not None} dat={dat_file is not None}, skipping")
        continue
    
    print(f"Processing FY{year_label}...")
    
    try:
        positions = parse_sas_positions(sas_file)
    except Exception as e:
        print(f"  ❌ SAS parse failed: {e}")
        continue
    
    available = {v: positions[v] for v in KEY_VARS if v in positions}
    missing = [v for v in KEY_VARS if v not in positions]
    if missing:
        print(f"  Missing vars: {missing}")
    
    print(f"  Found {len(available)}/{len(KEY_VARS)} key variables")
    
    colspecs = [(pos[0], pos[1]) for pos in available.values()]
    names = list(available.keys())
    
    try:
        df = pd.read_fwf(dat_file, colspecs=colspecs, names=names,
                         na_values=['.', ' .', '  .', '   .'])
        df["FISCAL_YEAR"] = int(year_label)
        
        # Ensure numeric types for key columns
        for col in names:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        all_frames.append(df)
        print(f"  → {len(df):,} cases")
    except Exception as e:
        print(f"  ❌ Parse failed: {e}")
        continue

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

# Ensure all KEY_VARS columns exist
for col in KEY_VARS:
    if col not in combined.columns:
        combined[col] = pd.NA

combined = combined[KEY_VARS + ["FISCAL_YEAR"]]

print(f"Total: {len(combined):,} cases across {combined['FISCAL_YEAR'].nunique()} years")
for year in sorted(combined["FISCAL_YEAR"].unique()):
    n = len(combined[combined["FISCAL_YEAR"] == year])
    print(f"  {int(year)}: {n:,} cases")

out_path = os.path.join(DATA_DIR, "combined_all_years.csv")
combined.to_csv(out_path, index=False)
print(f"\n✅ Saved to {out_path} ({os.path.getsize(out_path)/1024/1024:.1f} MB)")
