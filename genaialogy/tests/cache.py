"""File caching utilities for tests."""

import os
from pathlib import Path
import tempfile
import subprocess
from contextlib import contextmanager
import shutil


def download_file(file_url: str, output_filename: str):
    """Downloads a file if it does not already exist."""
    if not os.path.exists(output_filename):
        print(f"Downloading {output_filename}...")
        try:
            subprocess.run(['wget', '-q', file_url, '-O', output_filename], check=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to download {file_url}: {e}")
    else:
        print(f"{output_filename} already exists. Skipping download.")

def cached_file(request, url: str, file_path: str):
    """Cache a file from a URL."""
    temp_dir = tempfile.mkdtemp()
    local_file_path = Path(temp_dir, file_path)
    local_file_path.parent.mkdir(parents=True, exist_ok=True)
    download_file(url, str(local_file_path))
    print(f"Cached {file_path} to {local_file_path}")
    return local_file_path
