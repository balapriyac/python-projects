#!/usr/bin/env python3
"""
Directory Synchronizer
A two-way directory synchronization tool using only Python standard library.
"""

import os
import shutil
import hashlib
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from enum import Enum

class SyncAction(Enum):
    COPY_TO_TARGET = "copy_to_target"
    COPY_TO_SOURCE = "copy_to_source"
    UPDATE_TARGET = "update_target"
    UPDATE_SOURCE = "update_source"
    DELETE_FROM_TARGET = "delete_from_target"
    DELETE_FROM_SOURCE = "delete_from_source"
    CONFLICT = "conflict"

class DirectorySync:
    def __init__(self, source: str, target: str, sync_log_file: str = None):
        self.source = Path(source)
        self.target = Path(target)
        self.sync_log_file = sync_log_file or f"sync_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.actions: List[Dict] = []
        self.conflicts: List[Dict] = []
        
    def _get_file_hash(self, filepath: Path) -> str:
        """Calculate MD5 hash of a file."""
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (OSError, IOError):
            return ""
    
    def _get_file_info(self, filepath: Path, base_path: Path) -> Dict:
        """Get file information including relative path, size, and modification time."""
        try:
            stat = filepath.stat()
            rel_path = filepath.relative_to(base_path)
            return {
                'path': str(rel_path),
                'size': stat.st_size,
                'mtime': stat.st_mtime,
                'hash': self._get_file_hash(filepath),
                'full_path': str(filepath)
            }
        except (OSError, ValueError):
            return None
    
    def _scan_directory(self, directory: Path) -> Dict[str, Dict]:
        """Scan directory and return file information dictionary."""
        files = {}
        if not directory.exists():
            return files
        
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                filepath = Path(root) / filename
                file_info = self._get_file_info(filepath, directory)
                if file_info:
                    files[file_info['path']] = file_info
        
        return files
    
    def _determine_sync_actions(self, source_files: Dict, target_files: Dict) -> List[Dict]:
        """Determine what actions need to be taken for synchronization."""
        actions = []
        all_paths = set(source_files.keys()) | set(target_files.keys())
        
        for rel_path in all_paths:
            source_info = source_files.get(rel_path)
            target_info = target_files.get(rel_path)
            
            if source_info and not target_info:
                # File exists only in source
                actions.append({
                    'action': SyncAction.COPY_TO_TARGET,
                    'path': rel_path,
                    'source_info': source_info,
                    'target_info': None
                })
            
            elif target_info and not source_info:
                # File exists only in target
                actions.append({
                    'action': SyncAction.COPY_TO_SOURCE,
                    'path': rel_path,
                    'source_info': None,
                    'target_info': target_info
                })
            
            elif source_info and target_info:
                # File exists in both locations
                if source_info['hash'] != target_info['hash']:
                    # Files are different
                    if source_info['mtime'] > target_info['mtime']:
                        actions.append({
                            'action': SyncAction.UPDATE_TARGET,
                            'path': rel_path,
                            'source_info': source_info,
                            'target_info': target_info
                        })
                    elif target_info['mtime'] > source_info['mtime']:
                        actions.append({
                            'action': SyncAction.UPDATE_SOURCE,
                            'path': rel_path,
                            'source_info': source_info,
                            'target_info': target_info
                        })
                    else:
                        # Same modification time but different content - conflict
                        actions.append({
                            'action': SyncAction.CONFLICT,
                            'path': rel_path,
                            'source_info': source_info,
                            'target_info': target_info
                        })
        
        return actions
    
    def analyze(self) -> Tuple[List[Dict], List[Dict]]:
        """Analyze directories and determine sync actions."""
        print("Scanning source directory...")
        source_files = self._scan_directory(self.source)
        
        print("Scanning target directory...")
        target_files = self._scan_directory(self.target)
        
        print("Analyzing differences...")
        actions = self._determine_sync_actions(source_files, target_files)
        
        # Separate conflicts from regular actions
        regular_actions = [a for a in actions if a['action'] != SyncAction.CONFLICT]
        conflicts = [a for a in actions if a['action'] == SyncAction.CONFLICT]
        
        return regular_actions, conflicts
    
    def display_analysis(self, actions: List[Dict], conflicts: List[Dict]) -> None:
        """Display analysis results."""
        if not actions and not conflicts:
            print("Directories are already synchronized!")
            return
        
        action_counts = {}
        for action in actions:
            action_type = action['action']
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
        
        print("\n=== SYNC ANALYSIS ===")
        for action_type, count in action_counts.items():
            print(f"{action_type.value.replace('_', ' ').title()}: {count} files")
        
        if conflicts:
            print(f"Conflicts: {len(conflicts)} files")
        
        print(f"\nTotal changes: {len(actions)} files")
        
        # Show detailed actions
        if actions:
            print("\n=== PLANNED ACTIONS ===")
            for i, action in enumerate(actions[:10], 1):  # Show first 10
                action_desc = {
                    SyncAction.COPY_TO_TARGET: f"→ Copy to target: {action['path']}",
                    SyncAction.COPY_TO_SOURCE: f"← Copy to source: {action['path']}",
                    SyncAction.UPDATE_TARGET: f"→ Update target: {action['path']}",
                    SyncAction.UPDATE_SOURCE: f"← Update source: {action['path']}",
                }
                print(f"{i}. {action_desc[action['action']]}")
            
            if len(actions) > 10:
                print(f"... and {len(actions) - 10} more actions")
        
        if conflicts:
            print("\n=== CONFLICTS (manual resolution required) ===")
            for i, conflict in enumerate(conflicts, 1):
                print(f"{i}. {conflict['path']}")
                print(f"   Source: {datetime.fromtimestamp(conflict['source_info']['mtime'])}")
                print(f"   Target: {datetime.fromtimestamp(conflict['target_info']['mtime'])}")
    
    def _execute_action(self, action: Dict) -> bool:
        """Execute a single sync action."""
        try:
            rel_path = action['path']
            source_path = self.source / rel_path
            target_path = self.target / rel_path
            
            if action['action'] == SyncAction.COPY_TO_TARGET:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, target_path)
                
            elif action['action'] == SyncAction.COPY_TO_SOURCE:
                source_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target_path, source_path)
                
            elif action['action'] == SyncAction.UPDATE_TARGET:
                shutil.copy2(source_path, target_path)
                
            elif action['action'] == SyncAction.UPDATE_SOURCE:
                shutil.copy2(target_path, source_path)
            
            return True
            
        except Exception as e:
            print(f"Error executing action for {action['path']}: {e}")
            return False
    
    def sync(self, actions: List[Dict], dry_run: bool = False) -> Dict:
        """Execute synchronization actions."""
        if dry_run:
            print("DRY RUN - No changes will be made")
            return {"success": len(actions), "failed": 0, "skipped": 0}
        
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        print(f"\nExecuting {len(actions)} sync actions...")
        
        for i, action in enumerate(actions, 1):
            print(f"[{i}/{len(actions)}] Processing {action['path']}")
            
            if self._execute_action(action):
                results["success"] += 1
                # Log successful action
                action["timestamp"] = datetime.now().isoformat()
                action["status"] = "success"
                self.actions.append(action)
            else:
                results["failed"] += 1
        
        # Save sync log
        self._save_sync_log()
        
        print(f"\nSync complete!")
        print(f"Success: {results['success']}")
        print(f"Failed: {results['failed']}")
        
        return results
    
    def _save_sync_log(self) -> None:
        """Save sync log to file."""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "source": str(self.source),
            "target": str(self.target),
            "actions": [
                {
                    "action": action["action"].value if isinstance(action["action"], SyncAction) else str(action["action"]),
                    "path": action["path"],
                    "timestamp": action.get("timestamp"),
                    "status": action.get("status")
                }
                for action in self.actions
            ]
        }
        
        try:
            with open(self.sync_log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
            print(f"Sync log saved to: {self.sync_log_file}")
        except Exception as e:
            print(f"Failed to save sync log: {e}")
    
    def resolve_conflicts(self, conflicts: List[Dict]) -> List[Dict]:
        """Interactive conflict resolution."""
        if not conflicts:
            return []
        
        print(f"\n=== RESOLVING {len(conflicts)} CONFLICTS ===")
        resolved_actions = []
        
        for i, conflict in enumerate(conflicts, 1):
            print(f"\nConflict {i}/{len(conflicts)}: {conflict['path']}")
            
            source_info = conflict['source_info']
            target_info = conflict['target_info']
            
            print(f"Source: {self._format_file_info(source_info)}")
            print(f"Target: {self._format_file_info(target_info)}")
            
            while True:
                choice = input("Choose action (s)ource wins, (t)arget wins, (k)eep both, (s)kip: ").strip().lower()
                
                if choice == 's':
                    resolved_actions.append({
                        'action': SyncAction.UPDATE_TARGET,
                        'path': conflict['path'],
                        'source_info': source_info,
                        'target_info': target_info
                    })
                    break
                elif choice == 't':
                    resolved_actions.append({
                        'action': SyncAction.UPDATE_SOURCE,
                        'path': conflict['path'],
                        'source_info': source_info,
                        'target_info': target_info
                    })
                    break
                elif choice == 'k':
                    # Keep both by renaming one
                    backup_path = f"{conflict['path']}.conflict_backup_{int(datetime.now().timestamp())}"
                    print(f"Target file will be renamed to: {backup_path}")
                    
                    # First backup target, then copy source
                    resolved_actions.extend([
                        {
                            'action': 'rename_target',
                            'path': conflict['path'],
                            'new_path': backup_path,
                            'source_info': source_info,
                            'target_info': target_info
                        },
                        {
                            'action': SyncAction.UPDATE_TARGET,
                            'path': conflict['path'],
                            'source_info': source_info,
                            'target_info': target_info
                        }
                    ])
                    break
                elif choice == 'skip':
                    print("Skipping this conflict")
                    break
                else:
                    print("Invalid choice. Please enter s, t, k, or skip.")
        
        return resolved_actions
    
    def _format_file_info(self, file_info: Dict) -> str:
        """Format file info for display."""
        size = self._format_size(file_info['size'])
        mtime = datetime.fromtimestamp(file_info['mtime']).strftime('%Y-%m-%d %H:%M:%S')
        return f"{size}, modified {mtime}"
    
    @staticmethod
    def _format_size(size: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

def main():
    parser = argparse.ArgumentParser(description="Synchronize two directories")
    parser.add_argument('source', help='Source directory')
    parser.add_argument('target', help='Target directory')
    parser.add_argument('--dry-run', action='store_true', help='Show actions without executing')
    parser.add_argument('--log-file', help='Custom sync log file path')
    parser.add_argument('--auto-resolve', choices=['source', 'target'], 
                       help='Auto-resolve conflicts (source wins or target wins)')
    
    args = parser.parse_args()
    
    # Validate directories
    if not os.path.exists(args.source):
        print(f"Source directory does not exist: {args.source}")
        return
    
    # Create target directory if it doesn't exist
    os.makedirs(args.target, exist_ok=True)
    
    # Initialize synchronizer
    syncer = DirectorySync(args.source, args.target, args.log_file)
    
    # Analyze directories
    actions, conflicts = syncer.analyze()
    
    # Display analysis
    syncer.display_analysis(actions, conflicts)
    
    # Handle conflicts
    if conflicts and not args.auto_resolve:
        resolved_actions = syncer.resolve_conflicts(conflicts)
        actions.extend(resolved_actions)
    elif conflicts and args.auto_resolve:
        print(f"\nAuto-resolving {len(conflicts)} conflicts ({args.auto_resolve} wins)")
        for conflict in conflicts:
            if args.auto_resolve == 'source':
                actions.append({
                    'action': SyncAction.UPDATE_TARGET,
                    'path': conflict['path'],
                    'source_info': conflict['source_info'],
                    'target_info': conflict['target_info']
                })
            else:
                actions.append({
                    'action': SyncAction.UPDATE_SOURCE,
                    'path': conflict['path'],
                    'source_info': conflict['source_info'],
                    'target_info': conflict['target_info']
                })
    
    # Execute sync
    if actions:
        if not args.dry_run:
            confirm = input(f"\nProceed with synchronization of {len(actions)} files? (y/N): ").strip().lower()
            if confirm != 'y':
                print("Synchronization cancelled.")
                return
        
        syncer.sync(actions, dry_run=args.dry_run)
    else:
        print("No actions to perform.")

if __name__ == "__main__":
    main()
