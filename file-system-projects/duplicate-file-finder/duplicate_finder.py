#!/usr/bin/env python3
"""
Duplicate File Finder & Cleaner
A tool to find and manage duplicate files in directories using only Python standard library.
"""

import os
import hashlib
import argparse
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

class DuplicateFinder:
    def __init__(self, chunk_size: int = 8192):
        self.chunk_size = chunk_size
        self.size_groups: Dict[int, List[Path]] = defaultdict(list)
        self.duplicates: Dict[str, List[Path]] = defaultdict(list)
        
    def _get_file_hash(self, filepath: Path) -> str:
        """Calculate MD5 hash of a file."""
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(self.chunk_size):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (OSError, IOError) as e:
            print(f"Error reading {filepath}: {e}")
            return ""
    
    def _group_by_size(self, directories: List[str], extensions: Set[str] = None) -> None:
        """Group files by size for initial filtering."""
        print("Scanning directories and grouping by size...")
        
        for directory in directories:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    filepath = Path(root) / file
                    
                    # Filter by extensions if specified
                    if extensions and filepath.suffix.lower() not in extensions:
                        continue
                    
                    try:
                        size = filepath.stat().st_size
                        if size > 0:  # Skip empty files
                            self.size_groups[size].append(filepath)
                    except OSError:
                        continue
    
    def find_duplicates(self, directories: List[str], extensions: Set[str] = None) -> Dict[str, List[Path]]:
        """Find duplicate files in given directories."""
        self._group_by_size(directories, extensions)
        
        print("Calculating hashes for potential duplicates...")
        processed = 0
        total_candidates = sum(len(files) for files in self.size_groups.values() if len(files) > 1)
        
        for size, filepaths in self.size_groups.items():
            if len(filepaths) > 1:  # Only process files with potential duplicates
                for filepath in filepaths:
                    file_hash = self._get_file_hash(filepath)
                    if file_hash:
                        self.duplicates[file_hash].append(filepath)
                    processed += 1
                    
                    if processed % 100 == 0:
                        print(f"Processed {processed}/{total_candidates} files...")
        
        # Remove non-duplicates
        self.duplicates = {h: paths for h, paths in self.duplicates.items() if len(paths) > 1}
        return self.duplicates
    
    def display_duplicates(self) -> None:
        """Display found duplicates in a readable format."""
        if not self.duplicates:
            print("No duplicates found!")
            return
        
        total_duplicates = sum(len(paths) - 1 for paths in self.duplicates.values())
        total_wasted_space = sum(
            (len(paths) - 1) * paths[0].stat().st_size 
            for paths in self.duplicates.values()
        )
        
        print(f"\nFound {len(self.duplicates)} duplicate groups with {total_duplicates} duplicate files")
        print(f"Wasted space: {self._format_size(total_wasted_space)}\n")
        
        for i, (file_hash, filepaths) in enumerate(self.duplicates.items(), 1):
            size = filepaths[0].stat().st_size
            print(f"Group {i} ({len(filepaths)} files, {self._format_size(size)} each):")
            
            for j, filepath in enumerate(filepaths):
                marker = "[ORIGINAL]" if j == 0 else "[DUPLICATE]"
                print(f"  {marker} {filepath}")
            print()
    
    def save_report(self, output_file: str) -> None:
        """Save duplicate report to JSON file."""
        report = {
            "total_groups": len(self.duplicates),
            "total_duplicates": sum(len(paths) - 1 for paths in self.duplicates.values()),
            "duplicates": {
                h: [str(p) for p in paths] 
                for h, paths in self.duplicates.items()
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {output_file}")
    
    def interactive_cleanup(self) -> None:
        """Interactive mode to select which duplicates to delete."""
        if not self.duplicates:
            print("No duplicates to clean up!")
            return
        
        deleted_files = 0
        freed_space = 0
        
        for i, (file_hash, filepaths) in enumerate(self.duplicates.items(), 1):
            print(f"\nGroup {i}/{len(self.duplicates)} ({len(filepaths)} files):")
            
            for j, filepath in enumerate(filepaths):
                print(f"  {j+1}. {filepath}")
            
            while True:
                choice = input(f"\nSelect files to delete (1-{len(filepaths)}, 'a' for all except first, 's' to skip): ").strip().lower()
                
                if choice == 's':
                    break
                elif choice == 'a':
                    # Delete all except the first (original)
                    for filepath in filepaths[1:]:
                        try:
                            size = filepath.stat().st_size
                            filepath.unlink()
                            print(f"Deleted: {filepath}")
                            deleted_files += 1
                            freed_space += size
                        except OSError as e:
                            print(f"Error deleting {filepath}: {e}")
                    break
                else:
                    try:
                        indices = [int(x.strip()) - 1 for x in choice.split(',') if x.strip().isdigit()]
                        valid_indices = [i for i in indices if 0 <= i < len(filepaths)]
                        
                        if valid_indices:
                            for idx in sorted(valid_indices, reverse=True):
                                filepath = filepaths[idx]
                                try:
                                    size = filepath.stat().st_size
                                    filepath.unlink()
                                    print(f"Deleted: {filepath}")
                                    deleted_files += 1
                                    freed_space += size
                                except OSError as e:
                                    print(f"Error deleting {filepath}: {e}")
                            break
                        else:
                            print("Invalid selection. Try again.")
                    except ValueError:
                        print("Invalid input. Use numbers, 'a', or 's'.")
        
        print(f"\nCleanup complete!")
        print(f"Deleted {deleted_files} files")
        print(f"Freed {self._format_size(freed_space)} of space")
    
    @staticmethod
    def _format_size(size: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

def main():
    parser = argparse.ArgumentParser(description="Find and manage duplicate files")
    parser.add_argument('directories', nargs='+', help='Directories to scan')
    parser.add_argument('-e', '--extensions', help='File extensions to include (comma-separated)')
    parser.add_argument('-r', '--report', help='Save report to JSON file')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive cleanup mode')
    parser.add_argument('--dry-run', action='store_true', help='Show duplicates without cleanup option')
    
    args = parser.parse_args()
    
    # Validate directories
    valid_dirs = []
    for directory in args.directories:
        if os.path.isdir(directory):
            valid_dirs.append(directory)
        else:
            print(f"Warning: '{directory}' is not a valid directory")
    
    if not valid_dirs:
        print("No valid directories specified!")
        return
    
    # Parse extensions
    extensions = None
    if args.extensions:
        extensions = {f".{ext.strip().lower().lstrip('.')}" for ext in args.extensions.split(',')}
        print(f"Filtering for extensions: {', '.join(extensions)}")
    
    # Find duplicates
    finder = DuplicateFinder()
    duplicates = finder.find_duplicates(valid_dirs, extensions)
    
    # Display results
    finder.display_duplicates()
    
    # Save report if requested
    if args.report:
        finder.save_report(args.report)
    
    # Interactive cleanup
    if args.interactive and not args.dry_run and duplicates:
        confirm = input("\nProceed with interactive cleanup? (y/N): ").strip().lower()
        if confirm == 'y':
            finder.interactive_cleanup()

if __name__ == "__main__":
    main()
