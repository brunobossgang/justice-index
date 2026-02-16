"""
Parse all USSC FY2002-2024 .dat files and combine into one CSV.
"""
import os
import re
import zipfile
import pandas as pd

DATA_DIR = "data"

KEY_VARS = ["SENTTOT", "NEWRACE", "MONSEX", "AGE", "OFFGUIDE", "DISTRICT",
            "XMINSOR", "XMAXSOR", "CRIMHIST", "CRIMPTS", "CITIZEN",
            "NEWEDUC", "WEAPON", "SENTIMP", "DSPLEA", "INOUT", "PRESENT"]

def parse_sas_positions(sas_path):
    """Extract variable name -> (start, end) from SAS INPUT statement only."""
    with open(sas_path, 'r', errors='replace') as f:
        text = f.read()
    
    input_match = re.search(r'INPUT\s(.*?);', text, re.DOTALL | re.IGNORECASE)
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

# All years FY02-FY23 from .dat files
YEARS = {}
for y in range(2, 24):
    suffix = f"{y:02d}"
    YEARS[suffix] = f"20{suffix}"

all_frames = []

for suffix, year_label in sorted(YEARS.items()):
    extract_dir = os.path.join(DATA_DIR, f"sas_fy{suffix}")
    
    # Try to find and unzip if not extracted
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir, exist_ok=True)
        # Handle variant zip names
        zip_candidates = [
            os.path.join(DATA_DIR, f"opafy{suffix}nid.zip"),
            os.path.join(DATA_DIR, f"opafy{suffix}-nid.zip"),
        ]
        zip_path = None
        for zp in zip_candidates:
            if os.path.exists(zp):
                zip_path = zp
                break
        if zip_path:
            print(f"Unzipping {zip_path}...")
            try:
                with zipfile.ZipFile(zip_path, 'r') as z:
                    z.extractall(extract_dir)
            except Exception as e:
                print(f"  ⚠️  Failed to unzip {year_label}: {e}")
                continue
        else:
            print(f"⚠️  No zip found for FY{year_label}, skipping")
            continue
    
    # Find .sas and .dat files
    sas_file = None
    dat_file = None
    for f in os.listdir(extract_dir):
        fl = f.lower()
        if fl.endswith('.sas'):
            sas_file = os.path.join(extract_dir, f)
        if fl.endswith('.dat'):
            dat_file = os.path.join(extract_dir, f)
    
    if not sas_file or not dat_file:
        print(f"⚠️  FY{year_label}: missing .sas or .dat, skipping")
        continue
    
    print(f"Processing FY{year_label}...")
    
    try:
        positions = parse_sas_positions(sas_file)
    except Exception as e:
        print(f"  ⚠️  SAS parse failed: {e}")
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
        all_frames.append(df)
        print(f"  → {len(df):,} cases")
    except Exception as e:
        print(f"  ❌ Failed to read: {e}")
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
print(f"Total: {len(combined):,} cases across {combined['FISCAL_YEAR'].nunique()} years")

for year in sorted(combined["FISCAL_YEAR"].unique()):
    n = len(combined[combined["FISCAL_YEAR"] == year])
    print(f"  {int(year)}: {n:,} cases")

out_path = os.path.join(DATA_DIR, "combined_fy02_fy24.csv")
combined.to_csv(out_path, index=False)
print(f"\n✅ Saved to {out_path} ({os.path.getsize(out_path)/1024/1024:.1f} MB)")
