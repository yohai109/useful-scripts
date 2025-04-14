import os
import shutil
import re
from pathlib import Path
import argparse

def extract_episode_info(filename):
    # Extract show name, season, and episode from filename
    parts = filename.lower().split('.')
    show_name_parts = []
    season = None
    episode = None
    
    for part in parts:
        # Look for SxxExx pattern
        match = re.match(r's(\d+)e(\d+)', part.lower())
        if match:
            season = int(match.group(1))
            episode = int(match.group(2))
            break
        show_name_parts.append(part)
    
    show_name = ' '.join(show_name_parts)
    return show_name, season, episode

def get_user_choice(duplicates):
    print("\nFound duplicate episodes:")
    for i, file_info in enumerate(duplicates, 1):
        print(f"{i}. {file_info['filename']}")
        print(f"   Path: {file_info['path']}")
        print(f"   Size: {file_info['size'] / (1024*1024):.2f} MB")
    
    while True:
        try:
            choice = input("\nEnter the number of the file you want to keep (or 'all' to keep all): ")
            if choice.lower() == 'all':
                return None
            choice = int(choice)
            if 1 <= choice <= len(duplicates):
                return choice - 1
            print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number or 'all'.")

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

def organize_videos(root_dir, ignore_folder=None, cleanup=False, remove_duplicates=False):
    # Dictionary to store episode information
    episodes = {}
    
    # First pass: collect all video files and their information
    for root, dirs, files in os.walk(root_dir):
        # Skip the ignored folder if specified
        if ignore_folder and os.path.basename(root) == ignore_folder:
            dirs[:] = []  # Don't traverse into this directory
            continue
        
        for file in files:
            if file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
                try:
                    show_name, season, episode = extract_episode_info(file)
                    if not show_name or season is None or episode is None:
                        continue
                    
                    # Create a unique key for this episode
                    episode_key = (show_name, season, episode)
                    
                    # Store file information
                    file_info = {
                        'filename': file,
                        'path': os.path.join(root, file),
                        'size': os.path.getsize(os.path.join(root, file))
                    }
                    
                    if episode_key not in episodes:
                        episodes[episode_key] = []
                    episodes[episode_key].append(file_info)
                    
                except Exception as e:
                    print(f"Error processing {file}: {str(e)}")
    
    # Second pass: handle duplicates and move files
    for (show_name, season, episode), file_list in episodes.items():
        try:
            # Create show directory
            show_dir = os.path.join(root_dir, show_name)
            os.makedirs(show_dir, exist_ok=True)
            
            # Handle duplicates if option is enabled
            files_to_move = file_list
            if remove_duplicates and len(file_list) > 1:
                print(f"\nFound duplicates for {show_name} S{season:02d}E{episode:02d}:")
                choice = get_user_choice(file_list)
                if choice is not None:
                    # Keep only the chosen file
                    files_to_move = [file_list[choice]]
                    # Remove other files
                    for i, file_info in enumerate(file_list):
                        if i != choice:
                            print(f"Removing duplicate: {file_info['filename']}")
                            os.remove(file_info['path'])
            
            # Move the remaining files
            for file_info in files_to_move:
                source_path = file_info['path']
                dest_path = os.path.join(show_dir, file_info['filename'])
                
                if os.path.dirname(source_path) != show_dir:
                    print(f"Moving {file_info['filename']} to {show_name} folder")
                    shutil.move(source_path, dest_path)
                    
        except Exception as e:
            print(f"Error processing {show_name} S{season:02d}E{episode:02d}: {str(e)}")
    
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
    parser.add_argument('--remove-duplicates', '-d', action='store_true', help='Remove duplicate episodes after choosing which to keep')
    
    # Parse arguments
    args = parser.parse_args()
    root_dir = args.directory
    
    if os.path.isdir(root_dir):
        print(f"Organizing videos in {root_dir}...")
        organize_videos(root_dir, args.ignore, args.cleanup, args.remove_duplicates)
        print("Done!")
    else:
        print("Invalid directory path!")
