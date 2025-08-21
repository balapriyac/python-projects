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
2. Make them executable (optional):
   ```bash
   chmod +x directory_sync.py
   ```

## Example Workflows

### Setting Up Backup Sync

```bash
# Initial sync (dry run first)
python directory_sync.py ~/Documents ~/Backup --dry-run

# Execute the sync
python directory_sync.py ~/Documents ~/Backup

# Regular sync with auto-conflict resolution
python directory_sync.py ~/Documents ~/Backup --auto-resolve source
```

### Photo Library Management

```bash
# Sync photos between devices
python directory_sync.py ~/Pictures /media/external/Pictures
```


