
## Duplicate File Finder & Cleaner

A simple tool to find and manage duplicate files across directories.

### Features

- Uses file size pre-filtering and MD5 hashing for accurate duplicate detection
- Filter by file extensions
- Safely review and delete duplicates with confirmation
- Generate JSON reports of findings
- Shows how much storage space can be freed
- Preserves original files during cleanup

### Usage

```bash
# Basic usage - scan current directory
python duplicate_finder.py .

# Scan multiple directories
python duplicate_finder.py /home/user/Downloads /home/user/Documents

# Filter by file extensions
python duplicate_finder.py ~/Pictures -e jpg,png,gif

# Generate a report
python duplicate_finder.py ~/Downloads -r duplicates_report.json

# Interactive cleanup mode
python duplicate_finder.py ~/Downloads -i

# Dry run - just show duplicates
python duplicate_finder.py ~/Downloads --dry-run
```

### Example Output

```
Scanning directories and grouping by size...
Calculating hashes for potential duplicates...
Processed 500/500 files...

Found 5 duplicate groups with 12 duplicate files
Wasted space: 45.2 MB

Group 1 (3 files, 2.1 MB each):
  [ORIGINAL] /home/user/Downloads/photo1.jpg
  [DUPLICATE] /home/user/Downloads/photo1_copy.jpg
  [DUPLICATE] /home/user/Pictures/photo1.jpg

Group 2 (2 files, 15.5 MB each):
  [ORIGINAL] /home/user/Documents/video.mp4
  [DUPLICATE] /home/user/Downloads/video.mp4
```

### Command Line Options

- `directories`: One or more directories to scan
- `-e, --extensions`: Comma-separated list of file extensions to include
- `-r, --report`: Save detailed report to JSON file
- `-i, --interactive`: Enable interactive cleanup mode
- `--dry-run`: Show duplicates without cleanup option

---


- **Source wins** (`s`): Overwrite target with source file
- **Target wins** (`t`
