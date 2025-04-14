import os
import shutil
import re
from pathlib import Path
import argparse

def extract_show_name(filename):
    # Split by dots and find the part before s00e00 pattern
    parts = filename.lower().split('.')
    show_name_parts = []
    
    for part in parts:
        if re.match(r'[sS]\d+[eE]\d+', part):
            break
        show_name_parts.append(part)
    
    return ' '.join(show_name_parts)

def has_video_files_in_tree(directory):
    # Check if directory or any of its subdirectories have video files
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
                return True
    return False

def has_video_files(directory):
    # Check if directory has any video files directly in it (not in subdirectories)
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path) and file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
            return True
    return False

def organize_videos(root_dir, ignore_folder=None, cleanup=False):
    # Get all files recursively
    for root, dirs, files in os.walk(root_dir):
        # Skip the ignored folder if specified
        if ignore_folder and os.path.basename(root) == ignore_folder:
            dirs[:] = []  # Don't traverse into this directory
            continue
            
        for file in files:
            # Check if file is a video (you can add more extensions if needed)
            if file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
                try:
                    # Get the show name from the filename
                    show_name = extract_show_name(file)
                    if not show_name:
                        continue
                    
                    # Create show directory if it doesn't exist
                    show_dir = os.path.join(root_dir, show_name)
                    os.makedirs(show_dir, exist_ok=True)
                    
                    # Source and destination paths
                    source_path = os.path.join(root, file)
                    dest_path = os.path.join(show_dir, file)
                    
                    # Move the file if it's not already in the correct directory
                    if os.path.dirname(source_path) != show_dir:
                        print(f"Moving {file} to {show_name} folder")
                        shutil.move(source_path, dest_path)
                
                except Exception as e:
                    print(f"Error processing {file}: {str(e)}")
    
    # Cleanup subdirectories if requested
    if cleanup:
        print("\nCleaning up subdirectories...")
        # First identify all directories that should be preserved (have videos in their tree)
        preserve_dirs = set()
        for root, dirs, _ in os.walk(root_dir, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if has_video_files_in_tree(dir_path):
                    # Add this directory and all its parents to preserve list
                    current = dir_path
                    while current != root_dir:
                        preserve_dirs.add(current)
                        current = os.path.dirname(current)
        
        # Now remove directories that aren't in the preserve list
        for root, dirs, _ in os.walk(root_dir, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if dir_path not in preserve_dirs and dir_path != root_dir:
                        print(f"Removing directory with no video files in tree: {dir_path}")
                        shutil.rmtree(dir_path)
                except Exception as e:
                    print(f"Error removing directory {dir_path}: {str(e)}")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Organize video files into directories based on show names.')
    parser.add_argument('directory', help='Root directory containing video files to organize')
    parser.add_argument('--ignore', '-i', help='Folder name to ignore during organization', default=None)
    parser.add_argument('--cleanup', '-c', action='store_true', help='Delete empty subdirectories after moving files')
    
    # Parse arguments
    args = parser.parse_args()
    root_dir = args.directory
    
    if os.path.isdir(root_dir):
        print(f"Organizing videos in {root_dir}...")
        organize_videos(root_dir, args.ignore, args.cleanup)
        print("Done!")
    else:
        print("Invalid directory path!")
