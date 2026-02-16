"""
Re-download and parse missing/broken years, fix OFFTYPE2→OFFGUIDE.
Downloads one year at a time, parses, deletes raw files to save space.
"""
import os, re, subprocess, zipfile, glob
import pandas as pd

DATA_DIR = "data"

KEY_VARS = ["SENTTOT", "NEWRACE", "MONSEX", "AGE", "OFFGUIDE", "DISTRICT",
            "XMINSOR", "XMAXSOR", "CRIMHIST", "CRIMPTS", "CITIZEN",
            "NEWEDUC", "WEAPON", "SENTIMP", "DSPLEA", "INOUT", "PRESENT"]

# Also try OFFTYPE2 as fallback for OFFGUIDE
ALT_VARS = {"OFFGUIDE": "OFFTYPE2"}

# Years that need re-downloading/re-parsing
# FY02-10: need OFFTYPE2 mapped to OFFGUIDE
# FY06,11-17: were missing entirely
YEARS_TO_PROCESS = {
    "02": "2002", "03": "2003", "04": "2004", "05": "2005",
    "06": "2006", "07": "2007", "08": "2008", "09": "2009",
    "10": "2010", "11": "2011", "12": "2012", "13": "2013",
    "14": "2014", "15": "2015", "16": "2016", "17": "2017",
}

# Known USSC download URLs (patterns vary by year)
URL_PATTERNS = {
    "02": "https://www.ussc.gov/sites/default/files/zip/opafy02nid.zip",
    "03": "https://www.ussc.gov/sites/default/files/zip/opafy03nid.zip",
    "04": "https://www.ussc.gov/sites/default/files/zip/opafy04nid.zip",
    "05": "https://www.ussc.gov/sites/default/files/zip/opafy05nid.zip",
    "06": "https://www.ussc.gov/sites/default/files/zip/opafy06nid.zip",
    "07": "https://www.ussc.gov/sites/default/files/zip/opafy07nid.zip",
    "08": "https://www.ussc.gov/sites/default/files/zip/opafy08nid.zip",
    "09": "https://www.ussc.gov/sites/default/files/zip/opafy09nid.zip",
    "10": "https://www.ussc.gov/sites/default/files/zip/opafy10nid.zip",
    "11": "https://www.ussc.gov/sites/default/files/zip/opafy11nid.zip",
    "12": "https://www.ussc.gov/sites/default/files/zip/opafy12nid.zip",
    "13": "https://www.ussc.gov/sites/default/files/zip/opafy13nid.zip",
    "14": "https://www.ussc.gov/sites/default/files/zip/opafy14nid.zip",
    "15": "https://www.ussc.gov/sites/default/files/zip/opafy15nid.zip",
    "16": "https://www.ussc.gov/sites/default/files/zip/opafy16-nid.zip",
    "17": "https://www.ussc.gov/sites/default/files/zip/opafy17-nid.zip",
}


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


def process_year(suffix, year_label, url):
    tmp_dir = os.path.join(DATA_DIR, f"_tmp_fy{suffix}")
    os.makedirs(tmp_dir, exist_ok=True)
    zip_path = os.path.join(tmp_dir, f"fy{suffix}.zip")

    try:
        # Download
        print(f"  Downloading FY{year_label}...")
        r = subprocess.run(["curl", "-sL", "-o", zip_path, url], timeout=120)
        if r.returncode != 0 or not os.path.exists(zip_path) or os.path.getsize(zip_path) < 1000:
            print(f"  ❌ Download failed")
            return None

        # Extract
        print(f"  Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(tmp_dir)

        # Find .sas and .dat files
        sas_files = glob.glob(os.path.join(tmp_dir, "*.sas")) + glob.glob(os.path.join(tmp_dir, "**/*.sas"), recursive=True)
        dat_files = glob.glob(os.path.join(tmp_dir, "*.dat")) + glob.glob(os.path.join(tmp_dir, "**/*.dat"), recursive=True)

        if not sas_files or not dat_files:
            print(f"  ❌ Missing sas ({len(sas_files)}) or dat ({len(dat_files)})")
            return None

        sas_file = sas_files[0]
        dat_file = dat_files[0]

        # Parse SAS positions
        positions = parse_sas_positions(sas_file)

        # Build column mapping, using ALT_VARS for fallbacks
        available = {}
        for v in KEY_VARS:
            if v in positions:
                available[v] = positions[v]
            elif v in ALT_VARS and ALT_VARS[v] in positions:
                available[v] = positions[ALT_VARS[v]]  # Map OFFTYPE2 → OFFGUIDE

        missing = [v for v in KEY_VARS if v not in available]
        if missing:
            print(f"  Missing vars: {missing}")
        print(f"  Found {len(available)}/{len(KEY_VARS)} key variables")

        # Parse
        colspecs = [(pos[0], pos[1]) for pos in available.values()]
        names = list(available.keys())
        df = pd.read_fwf(dat_file, colspecs=colspecs, names=names,
                         na_values=['.', ' .', '  .', '   .'],
                         encoding='latin-1')
        for col in names:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df["FISCAL_YEAR"] = int(year_label)
        print(f"  → {len(df):,} cases")
        return df

    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return None
    finally:
        # Clean up immediately
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)


def main():
    frames = []

    for suffix, year_label in sorted(YEARS_TO_PROCESS.items()):
        if suffix not in URL_PATTERNS:
            print(f"⚠️  FY{year_label}: no URL, skipping")
            continue
        print(f"Processing FY{year_label}...")
        df = process_year(suffix, year_label, URL_PATTERNS[suffix])
        if df is not None and len(df) > 0:
            frames.append(df)

    if not frames:
        print("No new data parsed!")
        return

    new_data = pd.concat(frames, ignore_index=True)
    print(f"\nNew data: {len(new_data):,} cases across {new_data['FISCAL_YEAR'].nunique()} years")

    # Load existing data (FY2018-2024 from the old combined)
    existing = pd.read_csv(os.path.join(DATA_DIR, "combined_all_years.csv"), low_memory=False)
    # Keep only FY2018+ from existing (we're replacing everything before that)
    existing = existing[existing["FISCAL_YEAR"] >= 2018]
    print(f"Existing FY2018+: {len(existing):,} cases")

    # Combine
    combined = pd.concat([new_data, existing], ignore_index=True)
    for col in KEY_VARS:
        if col not in combined.columns:
            combined[col] = pd.NA
    combined = combined[KEY_VARS + ["FISCAL_YEAR"]]
    combined = combined.sort_values("FISCAL_YEAR").reset_index(drop=True)

    print(f"\nFinal: {len(combined):,} cases across {combined['FISCAL_YEAR'].nunique()} years")
    for yr in sorted(combined["FISCAL_YEAR"].unique()):
        n = len(combined[combined["FISCAL_YEAR"] == yr])
        offguide_pct = combined[combined["FISCAL_YEAR"] == yr]["OFFGUIDE"].notna().mean() * 100
        print(f"  FY{int(yr)}: {n:,} cases (OFFGUIDE: {offguide_pct:.0f}%)")

    out_path = os.path.join(DATA_DIR, "combined_all_years.csv")
    combined.to_csv(out_path, index=False)
    print(f"\n✅ Saved to {out_path} ({os.path.getsize(out_path)/1024/1024:.1f} MB)")

    # Clean up old file
    old = os.path.join(DATA_DIR, "combined_fy19_fy24.csv")
    if os.path.exists(old):
        os.remove(old)
        print(f"Removed old {old}")


if __name__ == "__main__":
    main()
