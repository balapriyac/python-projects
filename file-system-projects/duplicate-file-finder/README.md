
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
# File Management Tools

Two powerful file management tools built using only Python's standard library.

## 1. Duplicate File Finder & Cleaner

A comprehensive tool to find and manage duplicate files across directories.

### Features

- **Smart Detection**: Uses file size pre-filtering and MD5 hashing for accurate duplicate detection
- **Flexible Filtering**: Filter by file extensions
- **Interactive Cleanup**: Safely review and delete duplicates with confirmation
- **Detailed Reports**: Generate JSON reports of findings
- **Space Analysis**: Shows how much storage space can be freed
- **Safe Operations**: Preserves original files during cleanup

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

## 2. Directory Synchronizer

A bidirectional directory synchronization tool similar to Dropbox or rsync.

### Features

- **Two-Way Sync**: Bidirectional synchronization between directories
- **Conflict Detection**: Identifies and handles file conflicts intelligently
- **Smart Updates**: Uses modification time and content hash to determine sync direction
- **Interactive Conflict Resolution**: Manual resolution for conflicting files
- **Comprehensive Logging**: JSON logs of all sync operations
- **Dry Run Mode**: Preview changes before executing
- **Safe Operations**: Creates directories as needed, preserves file timestamps

### Usage

```bash
# Basic synchronization
python directory_sync.py /path/to/source /path/to/target

# Dry run - see what would be changed
python directory_sync.py /path/to/source /path/to/target --dry-run

# Custom log file
python directory_sync.py ~/Documents ~/Backup --log-file my_sync.json

# Auto-resolve conflicts (source wins)
python directory_sync.py ~/Documents ~/Backup --auto-resolve source

# Auto-resolve conflicts (target wins)
python directory_sync.py ~/Documents ~/Backup --auto-resolve target
```

### Example Output

```
Scanning source directory...
Scanning target directory...
Analyzing differences...

=== SYNC ANALYSIS ===
Copy to target: 15 files
Update target: 3 files
Copy to source: 2 files
Update source: 1 files
Conflicts: 2 files

Total changes: 21 files

=== PLANNED ACTIONS ===
1. → Copy to target: new_document.pdf
2. → Update target: modified_file.txt
3. ← Copy to source: target_only.docx
4. ← Update source: newer_in_target.xlsx

=== CONFLICTS (manual resolution required) ===
1. conflicted_file.txt
   Source: 2024-08-15 14:30:22
   Target: 2024-08-15 14:32:18
```

### Conflict Resolution

When conflicts are detected, you'll be prompted to choose:

- **Source wins** (`s`): Overwrite target with source file
- **Target wins** (`t`): Overwrite source with target file
- **Keep both** (`k`): Rename target file and copy source
- **Skip** (`skip`): Leave both files unchanged

### Command Line Options

- `source`: Source directory path
- `target`: Target directory path
- `--dry-run`: Preview actions without executing them
- `--log-file`: Custom path for sync log file
- `--auto-resolve`: Automatically resolve conflicts (`source` or `target` wins)

### Sync Logic

The synchronizer uses the following logic to determine actions:

1. **File exists only in source** → Copy to target
2. **File exists only in target** → Copy to source
3. **File exists in both locations**:
   - Same content (hash) → No action needed
   - Different content + source newer → Update target
   - Different content + target newer → Update source
   - Different content + same timestamp → Conflict (manual resolution)


### Setup

1. Download the Python file
2. Make it executable (optional):
   ```bash
   chmod +x duplicate_finder.py
   ```

## Example Workflows

### Cleaning Up Downloads Folder

```bash
# Find duplicates in downloads
python duplicate_finder.py ~/Downloads -r downloads_report.json

# Review and clean interactively
python duplicate_finder.py ~/Downloads -i

# Focus on specific file types
python duplicate_finder.py ~/Downloads -e pdf,doc,docx -i
```

### Photo Library Management

```bash
# Find duplicate photos
python duplicate_finder.py ~/Pictures -e jpg,jpeg,png,raw -r photo_duplicates.json
```


