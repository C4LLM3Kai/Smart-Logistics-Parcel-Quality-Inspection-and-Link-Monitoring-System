
import os
import zipfile
import shutil
import urllib.request
import ssl

# Ignore SSL errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = {
    "dataset1": "https://app.roboflow.com/ds/CqAgK8jfer?key=iRUAWCyo9I",
    "dataset2": "https://app.roboflow.com/ds/E2s7UTX5zt?key=r3qKi6Q5U9"
}

def download_and_inspect(name, url):
    print(f"Processing {name}...")
    zip_path = f"{name}.zip"
    extract_path = f"./temp_{name}"
    
    # Download
    print(f"Downloading {url}...")
    try:
        with urllib.request.urlopen(url, context=ctx) as response, open(zip_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
    except Exception as e:
        print(f"Download failed: {e}")
        return []
    
    # Extract data.yaml only
    found_names = []
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file in zip_ref.namelist():
                if file.endswith("data.yaml"):
                    # Read directly from zip without extracting
                    with zip_ref.open(file) as f:
                        content = f.read().decode('utf-8')
                        print(f"--- {name} Content ---")
                        # Simple parsing for 'names:'
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if 'names:' in line:
                                print(line)
                                # Check next lines for list or dict
                                for j in range(1, 10): # Check next 10 lines
                                    if i+j < len(lines):
                                        print(lines[i+j])
    except Exception as e:
        print(f"Zip read error: {e}")

    return found_names

c1 = download_and_inspect("dataset1", urls["dataset1"])
print("-" * 20)
c2 = download_and_inspect("dataset2", urls["dataset2"])
