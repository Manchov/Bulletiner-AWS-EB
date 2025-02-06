#!/usr/bin/env python3
"""
Package Lambda code + dependencies into function.zip for AWS Lambda deployment.
Skips __pycache__ directories to avoid Windows copytree errors and reduce package size.
"""

import os
import shutil
import zipfile
import sys

#TODO: After implementing lambda_core, modify the directories for packaging

# Adjust these paths as needed:
LAMBDA_CODE_DIR = "lambda_scraper"         # Contains your .py files, config.yaml, etc.
SITE_PACKAGES_DIR = "venv/Lib/site-packages"  # Where your pip dependencies are installed
OUTPUT_ZIP = "function_scrap.zip"
BUILD_DIR = "build_lambda"

def ignore_pycache(dir, contents):
    """
    A callable passed to 'ignore' parameter of shutil.copytree.
    Excludes any __pycache__ directories and their contents.
    """
    excluded = []
    for item in contents:
        if item == '__pycache__' or item.endswith('.pyc') or item.endswith('.pyo'):
            excluded.append(item)
    return excluded

def copy_contents(source, destination):
    """
    Copy contents from source to destination, skipping __pycache__ and .pyc files.
    If source is a directory, we do a directory-level copy (copytree).
    If it's a file, we copy it directly.
    """
    if os.path.isdir(source):
        # We can't copytree into an existing directory by default, so we must handle it differently
        for item in os.listdir(source):
            src_item = os.path.join(source, item)
            dst_item = os.path.join(destination, item)
            if os.path.isdir(src_item):
                shutil.copytree(src_item, dst_item, dirs_exist_ok=True, ignore=ignore_pycache)
            else:
                if item == '__pycache__' or item.endswith('.pyc') or item.endswith('.pyo'):
                    continue
                shutil.copy2(src_item, dst_item)
    else:
        # It's a file
        shutil.copy2(source, destination)

def package_lambda_function():
    # 1) Remove old zip if exists
    if os.path.exists(OUTPUT_ZIP):
        print(f"Removing old {OUTPUT_ZIP}...")
        os.remove(OUTPUT_ZIP)

    # 2) Recreate a fresh build directory
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.mkdir(BUILD_DIR)

    # 3) Copy code from LAMBDA_CODE_DIR to build_dir
    print(f"Copying code from {LAMBDA_CODE_DIR} to {BUILD_DIR} ...")
    copy_contents(LAMBDA_CODE_DIR, BUILD_DIR)

    # 4) Copy site-packages from venv into build_dir
    print(f"Copying site-packages from {SITE_PACKAGES_DIR} to {BUILD_DIR} ...")
    copy_contents(SITE_PACKAGES_DIR, BUILD_DIR)

    # 5) Zip everything in build_dir into function.zip (flattened structure)
    print(f"Zipping contents into {OUTPUT_ZIP} ...")
    with zipfile.ZipFile(OUTPUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(BUILD_DIR):
            # filter out __pycache__ from subdirectories
            dirs[:] = [d for d in dirs if d != '__pycache__']
            for filename in files:
                if filename.endswith('.pyc') or filename.endswith('.pyo'):
                    continue
                filepath = os.path.join(root, filename)
                arcname = os.path.relpath(filepath, start=BUILD_DIR)
                zf.write(filepath, arcname)

    print("Cleaning up temporary build directory.")
    shutil.rmtree(BUILD_DIR)

    print(f"Done! Created {OUTPUT_ZIP}.")

if __name__ == "__main__":
    try:
        package_lambda_function()
    except Exception as e:
        print(f"Error packaging Lambda function: {e}", file=sys.stderr)
        sys.exit(1)
