#!/usr/bin/env python3
"""
Download and setup ELK reasoner for use with OQuaRE.

This script downloads the ELK reasoner JAR file and places it in the libs directory
so it can be used with the OQuaRE tool.
"""

import os
import urllib.request
import sys
from urllib.parse import urlparse

def download_elk():
    """Download ELK reasoner JAR file."""
    
    # ELK reasoner download URL (version 0.4.3 - stable release)
    elk_url = "https://github.com/liveontologies/elk-reasoner/releases/download/v0.4.3/elk-distribution-0.4.3-owlapi-library.zip"
    expected_domain = "github.com"
    
    libs_dir = "./libs"
    elk_zip = os.path.join(libs_dir, "elk.zip")
    
    print("Downloading ELK reasoner...")
    
    try:
        # Validate URL is HTTPS and from expected domain
        parsed = urlparse(elk_url)
        if parsed.scheme != 'https' or parsed.netloc != expected_domain:
            print("✗ Error: Invalid URL. Only HTTPS URLs from github.com are allowed.")
            print(f"  Provided URL: {elk_url}")
            return False
        
        print(f"URL: {elk_url}")
        
        # Download the file
        urllib.request.urlretrieve(elk_url, elk_zip)
        print(f"✓ Downloaded to {elk_zip}")
        
        # Extract the ZIP file
        import zipfile
        print("Extracting ELK reasoner...")
        with zipfile.ZipFile(elk_zip, 'r') as zip_ref:
            zip_ref.extractall(libs_dir)
        print(f"✓ Extracted to {libs_dir}")
        
        # Clean up ZIP file
        os.remove(elk_zip)
        print("✓ Cleanup complete")
        
        print("\n" + "="*60)
        print("ELK reasoner setup complete!")
        print("="*60)
        print("\nNote: The OQuaRE tool may need to be modified to use ELK.")
        print("The current version appears to hardcode HermiT reasoner.")
        
        return True
        
    except Exception as e:
        print(f"✗ Error downloading ELK: {e}")
        return False

if __name__ == '__main__':
    success = download_elk()
    sys.exit(0 if success else 1)
