"""
Justice Index — Multi-Year Data Builder
Reads SAS (.sas7bdat) files from USSC FY2019-2024, extracts key columns,
and produces a single combined slim CSV for analysis.
"""
import os
import glob
import zipfile
import pandas as pd
import pyreadstat

DATA_DIR = "data"
OUT_FILE = "data/combined_fy19_fy24.csv"

KEY_COLS = [
    "DISTRICT", "OFFGUIDE", "SENTTOT", "SENTIMP",
    "XMINSOR", "XMAXSOR", "NEWRACE", "MONSEX", "AGE",
    "CITIZEN", "NEWEDUC", "CRIMHIST", "CRIMPTS", "WEAPON",
    "DSPLEA", "INOUT", "PRESENT",
]

YEARS = {
    "19": "FY2019", "20": "FY2020", "21": "FY2021",
    "22": "FY2022", "23": "FY2023", "24": "FY2024",
}

all_frames = []

for suffix, label in sorted(YEARS.items()):
    # FY2024 already has a CSV slim file
    if suffix == "24":
        slim_path = os.path.join(DATA_DIR, "individual_fy24", "slim.csv")
        if os.path.exists(slim_path):
            print(f"Loading {label} from existing slim CSV...")
            df = pd.read_csv(slim_path, low_memory=False)
            df["FISCAL_YEAR"] = int(f"20{suffix}")
            all_frames.append(df)
            print(f"  → {len(df):,} cases")
            continue

    zip_path = os.path.join(DATA_DIR, f"opafy{suffix}nid.zip")
    if not os.path.exists(zip_path):
        print(f"⚠️  {label}: zip not found, skipping")
        continue

    print(f"Processing {label}...")
    
    # Unzip
    extract_dir = os.path.join(DATA_DIR, f"sas_fy{suffix}")
    os.makedirs(extract_dir, exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(extract_dir)
    except zipfile.BadZipFile:
        print(f"  ⚠️  Bad zip file for {label}, skipping")
        continue
    
    # Find .sas7bdat file
    sas_files = glob.glob(os.path.join(extract_dir, "**", "*.sas7bdat"), recursive=True)
    if not sas_files:
        # Try .sav (SPSS)
        sas_files = glob.glob(os.path.join(extract_dir, "**", "*.sav"), recursive=True)
    
    if not sas_files:
        print(f"  ⚠️  No SAS/SPSS file found for {label}")
        print(f"      Files: {os.listdir(extract_dir)}")
        continue
    
    sas_file = sas_files[0]
    ext = os.path.splitext(sas_file)[1].lower()
    print(f"  Reading {os.path.basename(sas_file)}...")
    
    try:
        if ext == ".sas7bdat":
            df, meta = pyreadstat.read_sas7bdat(sas_file, usecols=[c for c in KEY_COLS])
        elif ext == ".sav":
            df, meta = pyreadstat.read_sav(sas_file, usecols=[c for c in KEY_COLS])
        else:
            print(f"  ⚠️  Unknown format: {ext}")
            continue
    except Exception as e:
        # If usecols fails (column names differ), read all and filter
        print(f"  Trying full read (column mismatch)...")
        try:
            if ext == ".sas7bdat":
                df, meta = pyreadstat.read_sas7bdat(sas_file)
            else:
                df, meta = pyreadstat.read_sav(sas_file)
            available = [c for c in KEY_COLS if c in df.columns]
            df = df[available]
        except Exception as e2:
            print(f"  ❌ Failed to read {label}: {e2}")
            continue
    
    df["FISCAL_YEAR"] = int(f"20{suffix}")
    all_frames.append(df)
    print(f"  → {len(df):,} cases, {len(df.columns)} columns")

if not all_frames:
    print("❌ No data loaded!")
    exit(1)

print(f"\nCombining {len(all_frames)} years...")
combined = pd.concat(all_frames, ignore_index=True)
print(f"Total: {len(combined):,} cases across {combined['FISCAL_YEAR'].nunique()} years")
print(f"Years: {sorted(combined['FISCAL_YEAR'].unique())}")

# Quick sanity check
for year in sorted(combined["FISCAL_YEAR"].unique()):
    n = len(combined[combined["FISCAL_YEAR"] == year])
    print(f"  {year}: {n:,} cases")

combined.to_csv(OUT_FILE, index=False)
print(f"\n✅ Saved to {OUT_FILE} ({os.path.getsize(OUT_FILE)/1024/1024:.1f} MB)")
