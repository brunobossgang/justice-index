"""Download and parse USSC Individual Offender datafiles FY2002-2018."""
import os
import subprocess
import zipfile
import re
import pandas as pd

DATA_DIR = "data"

# URLs from USSC website (note FY16/17 have dashes)
URLS = {
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
    "18": "https://www.ussc.gov/sites/default/files/zip/opafy18nid.zip",
}

KEY_VARS = ["SENTTOT", "NEWRACE", "MONSEX", "AGE", "OFFGUIDE", "DISTRICT",
            "XMINSOR", "XMAXSOR", "CRIMHIST", "CRIMPTS", "CITIZEN",
            "NEWEDUC", "WEAPON", "SENTIMP", "DSPLEA", "INOUT", "PRESENT"]


def parse_sas_positions(sas_path):
    """Extract variable name -> (start, end) from SAS INPUT statement only."""
    with open(sas_path, 'r', errors='replace') as f:
        text = f.read()
    
    # Restrict to INPUT section only
    input_match = re.search(r'INPUT\s(.*?);', text, re.DOTALL | re.IGNORECASE)
    if not input_match:
        raise ValueError(f"No INPUT section found in {sas_path}")
    input_text = input_match.group(1)
    
    positions = {}
    # Range columns: VARNAME  start-end  or  VARNAME $ start-end
    for m in re.finditer(r'(\w+)\s+\$?\s*(\d+)-(\d+)', input_text):
        name = m.group(1).upper()
        start = int(m.group(2)) - 1
        end = int(m.group(3))
        positions[name] = (start, end)
    
    # Single-column
    for m in re.finditer(r'(\w+)\s+\$?\s*(\d+)(?:\s|$)', input_text):
        name = m.group(1).upper()
        pos = int(m.group(2))
        if name not in positions and pos > 10:
            positions[name] = (pos - 1, pos)
    
    return positions


def download_and_extract(suffix, url):
    """Download zip and extract to data/sas_fyXX/."""
    zip_name = os.path.basename(url)
    zip_path = os.path.join(DATA_DIR, zip_name)
    extract_dir = os.path.join(DATA_DIR, f"sas_fy{suffix}")
    
    if os.path.exists(extract_dir) and any(f.endswith('.dat') for f in os.listdir(extract_dir)):
        print(f"  Already extracted FY20{suffix}")
        return extract_dir
    
    if not os.path.exists(zip_path):
        print(f"  Downloading {zip_name}...")
        subprocess.run(["curl", "-L", "-o", zip_path, url], check=True, 
                       capture_output=True)
    
    os.makedirs(extract_dir, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(extract_dir)
    except zipfile.BadZipFile:
        print(f"  ⚠️ Bad zip for FY20{suffix}")
        return None
    
    return extract_dir


def find_file(directory, ext):
    """Find file with given extension recursively."""
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.lower().endswith(ext):
                return os.path.join(root, f)
    return None


def process_year(suffix):
    """Download, extract, and parse one year."""
    url = URLS[suffix]
    year = int(f"20{suffix}")
    print(f"\n{'='*50}")
    print(f"Processing FY{year}...")
    
    extract_dir = download_and_extract(suffix, url)
    if not extract_dir:
        return None
    
    # Find .sas and .dat files
    sas_file = find_file(extract_dir, '.sas')
    dat_file = find_file(extract_dir, '.dat')
    
    if not sas_file or not dat_file:
        # List what we got
        all_files = []
        for root, dirs, files in os.walk(extract_dir):
            for f in files:
                all_files.append(os.path.join(root, f))
        print(f"  Files found: {all_files}")
        if not sas_file:
            print(f"  ⚠️ No .sas file found")
        if not dat_file:
            print(f"  ⚠️ No .dat file found")
        return None
    
    print(f"  SAS: {os.path.basename(sas_file)}")
    print(f"  DAT: {os.path.basename(dat_file)}")
    
    # Parse positions
    try:
        positions = parse_sas_positions(sas_file)
    except ValueError as e:
        print(f"  ⚠️ {e}")
        return None
    
    available = {v: positions[v] for v in KEY_VARS if v in positions}
    missing = [v for v in KEY_VARS if v not in positions]
    if missing:
        print(f"  Missing vars: {missing}")
    print(f"  Found {len(available)}/{len(KEY_VARS)} key variables")
    
    if len(available) < 5:
        print(f"  ⚠️ Too few variables, skipping")
        return None
    
    colspecs = [(pos[0], pos[1]) for pos in available.values()]
    names = list(available.keys())
    
    try:
        df = pd.read_fwf(dat_file, colspecs=colspecs, names=names,
                         na_values=['.', ' .', '  .', '   .'],
                         encoding='latin-1')
    except Exception as e:
        print(f"  ⚠️ Error reading .dat: {e}")
        return None
    df["FISCAL_YEAR"] = year
    print(f"  → {len(df):,} cases")
    return df


if __name__ == "__main__":
    frames = []
    for suffix in sorted(URLS.keys()):
        df = process_year(suffix)
        if df is not None:
            frames.append(df)
    
    if frames:
        combined = pd.concat(frames, ignore_index=True)
        out_path = os.path.join(DATA_DIR, "combined_fy02_fy18.csv")
        combined.to_csv(out_path, index=False)
        print(f"\n✅ Saved {len(combined):,} cases across {combined['FISCAL_YEAR'].nunique()} years to {out_path}")
        for year in sorted(combined["FISCAL_YEAR"].unique()):
            n = len(combined[combined["FISCAL_YEAR"] == year])
            print(f"  {int(year)}: {n:,} cases")
    else:
        print("❌ No data loaded!")
