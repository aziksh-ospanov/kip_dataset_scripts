#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import sys
from pathlib import Path
from tqdm import tqdm  # pip install tqdm
from imagededup.methods import PHash, DHash, WHash, AHash

# Map string arguments to library classes
HASH_METHODS = {
    'phash': PHash,
    'dhash': DHash,
    'whash': WHash,
    'ahash': AHash
}

def parse_args():
    parser = argparse.ArgumentParser(
        description="Find and remove duplicate images in a class-structured directory."
    )
    parser.add_argument(
        '--input_dir', 
        type=str, 
        required=True, 
        help="Path to the root directory containing class folders (e.g., /data/dataset)"
    )
    parser.add_argument(
        '--method', 
        type=str, 
        default='phash', 
        choices=HASH_METHODS.keys(), 
        help="Hashing method to use (default: phash)"
    )
    parser.add_argument(
        '--threshold', 
        type=int, 
        default=10, 
        help="Hamming distance threshold. Lower is stricter (default: 10)"
    )
    parser.add_argument(
        '--delete', 
        action='store_true', 
        help="If set, duplicates will be permanently DELETED. Otherwise, performs a dry run."
    )
    return parser.parse_args()

def get_image_files(root_dir):
    """
    Recursively finds all image files in the root_dir.
    """
    extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    image_paths = []
    
    print(f"Scanning {root_dir} for images...")
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if Path(file).suffix.lower() in extensions:
                image_paths.append(os.path.join(root, file))
    
    print(f"Found {len(image_paths)} images.")
    return image_paths

def generate_encodings(hasher, image_paths):
    """
    Generates encodings for a list of image paths using the specified hasher.
    """
    encodings = {}
    print("Generating image hashes...")
    
    # We loop manually to handle full paths correctly across nested subdirectories
    for img_path in tqdm(image_paths):
        try:
            # We use the full path as the key to ensure uniqueness across folders
            hash_str = hasher.encode_image(image_file=img_path)
            encodings[img_path] = hash_str
        except Exception as e:
            # print(f"Could not encode {img_path}: {e}")
            continue
            
    return encodings

def find_and_process_duplicates(encodings, hasher, threshold, delete_mode):
    """
    Finds duplicates and either lists them or deletes them.
    """
    print("Finding duplicates...")
    duplicates = hasher.find_duplicates(encoding_map=encodings, max_distance_threshold=threshold, scores=False)
    
    files_to_remove = set()
    kept_files = set()
    
    # duplicates is a dict: {filename: [dup1, dup2, ...]}
    # We sort keys to ensure deterministic processing order
    sorted_filenames = sorted(duplicates.keys())
    
    for filename in sorted_filenames:
        # If this file is already marked for removal, skip it (it's a duplicate of a previous file)
        if filename in files_to_remove:
            continue
            
        dups = duplicates.get(filename, [])
        
        if not dups:
            continue
            
        # If we are here, 'filename' is the "original" we keep.
        kept_files.add(filename)
        
        # Mark all its found duplicates for removal
        for dup in dups:
            if dup != filename and dup not in files_to_remove and dup not in kept_files:
                files_to_remove.add(dup)

    # Action Phase
    print(f"\n--- Result Summary ---")
    print(f"Total images processed: {len(encodings)}")
    print(f"Unique images to keep:  {len(encodings) - len(files_to_remove)}")
    print(f"Duplicates found:       {len(files_to_remove)}")
    
    if len(files_to_remove) == 0:
        return

    if delete_mode:
        print("\n!!! DELETING DUPLICATES !!!")
        for file_path in files_to_remove:
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except OSError as e:
                print(f"Error deleting {file_path}: {e}")
    else:
        print("\n--- Dry Run (Files that would be deleted) ---")
        for file_path in files_to_remove:
            print(f"Would delete: {file_path}")
        print("\nRun with --delete to actually remove these files.")

def main():
    args = parse_args()
    
    # 1. Initialize Hasher
    hasher_class = HASH_METHODS[args.method]
    hasher = hasher_class()
    
    # 2. Get Files
    image_paths = get_image_files(args.input_dir)
    
    if not image_paths:
        print("No images found. Exiting.")
        return

    # 3. Encode
    encodings = generate_encodings(hasher, image_paths)
    
    # 4. Find and Process
    find_and_process_duplicates(encodings, hasher, args.threshold, args.delete)

if __name__ == '__main__':
    main()