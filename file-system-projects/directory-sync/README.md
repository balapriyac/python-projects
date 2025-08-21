## Directory Synchronizer

A bidirectional directory synchronization tool built using the Python standard library.

### Features

- Bidirectional synchronization between directories
- Identifies and handles file conflicts intelligently
- Uses modification time and content hash to determine sync direction
- Manual resolution for conflicting files
- JSON logs of all sync operations
- Preview changes before executing
- Creates directories as needed, preserves file timestamps

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

