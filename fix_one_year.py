"""
Process a single USSC year with minimal RAM usage.
Reads .dat file line-by-line instead of loading into pandas.
Usage: python fix_one_year.py 06
"""
import os, re, sys, subprocess, zipfile, glob, shutil, csv

DATA_DIR = "data"
KEY_VARS = ["SENTTOT", "NEWRACE", "MONSEX", "AGE", "OFFGUIDE", "DISTRICT",
            "XMINSOR", "XMAXSOR", "CRIMHIST", "CRIMPTS", "CITIZEN",
            "NEWEDUC", "WEAPON", "SENTIMP", "DSPLEA", "INOUT", "PRESENT"]
ALT_VARS = {"OFFGUIDE": "OFFTYPE2"}

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
        positions[name] = (int(m.group(2)) - 1, int(m.group(3)))
    for m in re.finditer(r'(\w+)\s+\$?\s*(\d+)(?:\s|$)', input_text):
        name = m.group(1).upper()
        pos = int(m.group(2))
        if name not in positions and pos > 10:
            positions[name] = (pos - 1, pos)
    return positions

suffix = sys.argv[1]
year = 2000 + int(suffix)

urls = {
    "16": "https://www.ussc.gov/sites/default/files/zip/opafy16-nid.zip",
    "17": "https://www.ussc.gov/sites/default/files/zip/opafy17-nid.zip",
}
url = urls.get(suffix, f"https://www.ussc.gov/sites/default/files/zip/opafy{suffix}nid.zip")

tmp_dir = os.path.join(DATA_DIR, f"_tmp_fy{suffix}")
os.makedirs(tmp_dir, exist_ok=True)
zip_path = os.path.join(tmp_dir, "data.zip")

try:
    # Download
    print(f"Downloading FY{year}...", flush=True)
    subprocess.run(["curl", "-sL", "--max-time", "300", "-o", zip_path, url], timeout=310, check=True)
    print(f"  Downloaded: {os.path.getsize(zip_path)/1e6:.1f}MB", flush=True)
    
    # Extract
    print(f"  Extracting...", flush=True)
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(tmp_dir)
    # Delete zip immediately
    os.remove(zip_path)
    
    sas_files = glob.glob(os.path.join(tmp_dir, "**/*.sas"), recursive=True) + glob.glob(os.path.join(tmp_dir, "*.sas"))
    dat_files = glob.glob(os.path.join(tmp_dir, "**/*.dat"), recursive=True) + glob.glob(os.path.join(tmp_dir, "*.dat"))
    
    if not sas_files or not dat_files:
        print(f"  ❌ Missing files: sas={len(sas_files)} dat={len(dat_files)}")
        sys.exit(1)
    
    sas_file = sas_files[0]
    dat_file = dat_files[0]
    print(f"  DAT size: {os.path.getsize(dat_file)/1e6:.0f}MB", flush=True)
    
    # Parse SAS positions
    positions = parse_sas_positions(sas_file)
    
    # Build column mapping with fallbacks
    available = {}
    for v in KEY_VARS:
        if v in positions:
            available[v] = positions[v]
        elif v in ALT_VARS and ALT_VARS[v] in positions:
            available[v] = positions[ALT_VARS[v]]
    
    missing = [v for v in KEY_VARS if v not in available]
    print(f"  Found {len(available)}/{len(KEY_VARS)} vars. Missing: {missing}", flush=True)
    
    # Read line by line — minimal RAM
    out_path = os.path.join(DATA_DIR, f"slim_fy{suffix}.csv")
    cols = list(available.keys()) + ["FISCAL_YEAR"]
    row_count = 0
    
    print(f"  Parsing line by line...", flush=True)
    with open(dat_file, 'r', encoding='latin-1', errors='replace') as fin, \
         open(out_path, 'w', newline='') as fout:
        writer = csv.writer(fout)
        writer.writerow(cols)
        
        for line in fin:
            row = []
            for var_name, (start, end) in available.items():
                if start < len(line):
                    val = line[start:min(end, len(line))].strip()
                    if val in ('', '.', ' .', '  .', '   .'):
                        row.append('')
                    else:
                        row.append(val)
                else:
                    row.append('')
            row.append(str(year))
            writer.writerow(row)
            row_count += 1
            if row_count % 20000 == 0:
                print(f"    {row_count:,} rows...", flush=True)
    
    print(f"✅ FY{year}: {row_count:,} cases → {out_path} ({os.path.getsize(out_path)/1e6:.1f}MB)", flush=True)

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)
