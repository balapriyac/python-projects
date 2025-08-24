#!/usr/bin/env python3
"""
Configuration Manager - A practical tool for managing JSON configurations
with validation, schema checking, and template generation.

Features:
- Load and validate JSON configurations
- Generate configuration templates
- Merge configurations with defaults
- Environment-specific config management
- Configuration backup and restore
- Schema validation with custom rules
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import re


class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass


class ConfigManager:
    """
    A comprehensive configuration manager for JSON-based application configs.
    """
    
    def __init__(self, config_dir: str = "configs"):
        """
        Initialize the ConfigManager.
        
        Args:
            config_dir: Directory to store configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Default schema for basic validation
        self.default_schema = {
            "required_fields": [],
            "field_types": {},
            "field_constraints": {}
        }
    
    def create_template(self, template_name: str, template_data: Dict[str, Any]) -> str:
        """
        Create a configuration template.
        
        Args:
            template_name: Name of the template
            template_data: Template configuration data
            
        Returns:
            Path to the created template file
        """
        template_path = self.config_dir / f"{template_name}_template.json"
        
        # Add metadata to template
        template_with_meta = {
            "_metadata": {
                "template_name": template_name,
                "created": datetime.now().isoformat(),
                "description": f"Template for {template_name} configuration"
            },
            "config": template_data
        }
        
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template_with_meta, f, indent=2, ensure_ascii=False)
        
        print(f"Template created: {template_path}")
        return str(template_path)
    
    def load_config(self, config_file: str, validate: bool = True) -> Dict[str, Any]:
        """
        Load and optionally validate a configuration file.
        
        Args:
            config_file: Path to the configuration file
            validate: Whether to perform validation
            
        Returns:
            Configuration dictionary
            
        Raises:
            ConfigurationError: If file doesn't exist or validation fails
        """
        config_path = Path(config_file)
        
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_file}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in {config_file}: {e}")
        
        if validate:
            self.validate_config(config, config_file)
        
        return config
    
    def save_config(self, config: Dict[str, Any], config_file: str, 
                   create_backup: bool = True) -> str:
        """
        Save configuration to file with optional backup.
        
        Args:
            config: Configuration dictionary
            config_file: Path to save the configuration
            create_backup: Whether to create a backup of existing file
            
        Returns:
            Path to the saved configuration file
        """
        config_path = Path(config_file)
        
        # Create backup if file exists and backup is requested
        if config_path.exists() and create_backup:
            self.backup_config(config_file)
        
        # Ensure parent directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")
        
        print(f"Configuration saved: {config_path}")
        return str(config_path)
    
    def validate_config(self, config: Dict[str, Any], config_name: str = "config"):
        """
        Validate configuration against basic rules.
        
        Args:
            config: Configuration to validate
            config_name: Name for error reporting
            
        Raises:
            ConfigurationError: If validation fails
        """
        errors = []
        
        # Check for required fields
        required_fields = ["app_name", "version"]  # Basic requirements
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Validate specific field types and constraints
        validations = {
            "version": lambda v: isinstance(v, str) and re.match(r'^\d+\.\d+\.\d+$', v),
            "app_name": lambda v: isinstance(v, str) and len(v) > 0,
            "port": lambda v: isinstance(v, int) and 1 <= v <= 65535,
            "debug": lambda v: isinstance(v, bool)
        }
        
        for field, validator in validations.items():
            if field in config and not validator(config[field]):
                errors.append(f"Invalid value for {field}: {config[field]}")
        
        if errors:
            raise ConfigurationError(f"Validation failed for {config_name}:\n" + 
                                   "\n".join(f"  - {error}" for error in errors))
    
    def merge_configs(self, base_config: Dict[str, Any], 
                     override_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge two configurations, with override taking precedence.
        
        Args:
            base_config: Base configuration
            override_config: Override configuration
            
        Returns:
            Merged configuration
        """
        def deep_merge(base: Dict, override: Dict) -> Dict:
            result = base.copy()
            for key, value in override.items():
                if (key in result and isinstance(result[key], dict) 
                    and isinstance(value, dict)):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        return deep_merge(base_config, override_config)
    
    def get_environment_config(self, base_config_file: str, 
                             environment: str) -> Dict[str, Any]:
        """
        Load environment-specific configuration.
        
        Args:
            base_config_file: Base configuration file
            environment: Environment name (dev, staging, prod, etc.)
            
        Returns:
            Environment-specific configuration
        """
        base_config = self.load_config(base_config_file)
        
        # Try to load environment-specific overrides
        env_config_file = (Path(base_config_file).parent / 
                          f"{Path(base_config_file).stem}.{environment}.json")
        
        if env_config_file.exists():
            env_config = self.load_config(str(env_config_file))
            return self.merge_configs(base_config, env_config)
        
        return base_config
    
    def backup_config(self, config_file: str) -> str:
        """
        Create a backup of a configuration file.
        
        Args:
            config_file: Path to the configuration file
            
        Returns:
            Path to the backup file
        """
        config_path = Path(config_file)
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_file}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{config_path.stem}_{timestamp}.json"
        backup_path = self.backup_dir / backup_filename
        
        shutil.copy2(config_path, backup_path)
        print(f"Backup created: {backup_path}")
        return str(backup_path)
    
    def list_configs(self) -> List[str]:
        """
        List all configuration files in the config directory.
        
        Returns:
            List of configuration file paths
        """
        configs = []
        for file_path in self.config_dir.glob("*.json"):
            if not file_path.name.endswith("_template.json"):
                configs.append(str(file_path))
        return sorted(configs)
    
    def list_backups(self) -> List[str]:
        """
        List all backup files.
        
        Returns:
            List of backup file paths
        """
        return sorted([str(f) for f in self.backup_dir.glob("*.json")])
    
    def generate_sample_configs(self):
        """Generate sample configurations for demonstration."""
        
        # Main application config
        app_config = {
            "app_name": "MyWebApp",
            "version": "1.0.0",
            "debug": False,
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "myapp_db",
                "user": "myapp_user",
                "password": "change_me"
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8080,
                "workers": 4
            },
            "logging": {
                "level": "INFO",
                "file": "app.log",
                "max_size": "10MB",
                "backup_count": 5
            },
            "features": {
                "enable_caching": True,
                "enable_metrics": True,
                "enable_auth": True
            }
        }
        
        # Development environment overrides
        dev_config = {
            "debug": True,
            "database": {
                "name": "myapp_dev_db"
            },
            "server": {
                "port": 8000,
                "workers": 1
            },
            "logging": {
                "level": "DEBUG"
            }
        }
        
        # Production environment overrides
        prod_config = {
            "debug": False,
            "database": {
                "host": "prod-db.example.com",
                "name": "myapp_production"
            },
            "server": {
                "workers": 8
            },
            "features": {
                "enable_metrics": True
            }
        }
        
        # Save configurations
        self.save_config(app_config, self.config_dir / "app.json")
        self.save_config(dev_config, self.config_dir / "app.dev.json")
        self.save_config(prod_config, self.config_dir / "app.prod.json")
        
        # Create template
        template_config = {
            "app_name": "{{APP_NAME}}",
            "version": "{{VERSION}}",
            "debug": "{{DEBUG_MODE}}",
            "database": {
                "host": "{{DB_HOST}}",
                "port": "{{DB_PORT}}",
                "name": "{{DB_NAME}}",
                "user": "{{DB_USER}}",
                "password": "{{DB_PASSWORD}}"
            }
        }
        self.create_template("webapp", template_config)


def main():
    """Demonstration of the ConfigManager functionality."""
    
    print("=== Configuration Manager Demo ===\n")
    
    # Initialize ConfigManager
    config_mgr = ConfigManager("example_configs")
    
    # Generate sample configurations
    print("1. Generating sample configurations...")
    config_mgr.generate_sample_configs()
    print()
    
    # List configurations
    print("2. Available configurations:")
    for config in config_mgr.list_configs():
        print(f"   - {config}")
    print()
    
    # Load and validate configuration
    print("3. Loading and validating main config...")
    try:
        app_config = config_mgr.load_config("example_configs/app.json")
        print(f"   ✓ Loaded config for: {app_config['app_name']} v{app_config['version']}")
    except ConfigurationError as e:
        print(f"   ✗ Error: {e}")
    print()
    
    # Environment-specific configuration
    print("4. Loading environment-specific configurations...")
    for env in ["dev", "prod"]:
        try:
            env_config = config_mgr.get_environment_config(
                "example_configs/app.json", env
            )
            print(f"   ✓ {env.upper()}: Debug={env_config['debug']}, "
                  f"Port={env_config['server']['port']}, "
                  f"DB={env_config['database']['name']}")
        except Exception as e:
            print(f"   ✗ {env.upper()}: {e}")
    print()
    
    # Configuration backup
    print("5. Creating backup...")
    try:
        backup_path = config_mgr.backup_config("example_configs/app.json")
        print(f"   ✓ Backup created successfully")
    except Exception as e:
        print(f"   ✗ Backup failed: {e}")
    print()
    
    # List backups
    print("6. Available backups:")
    for backup in config_mgr.list_backups():
        print(f"   - {backup}")
    print()
    
    # Configuration modification example
    print("7. Modifying and saving configuration...")
    try:
        modified_config = app_config.copy()
        modified_config["version"] = "1.1.0"
        modified_config["features"]["enable_monitoring"] = True
        
        config_mgr.save_config(
            modified_config, 
            "example_configs/app_modified.json"
        )
        print("   ✓ Modified configuration saved")
    except Exception as e:
        print(f"   ✗ Failed to save: {e}")
    
    print("\n=== Demo completed ===")
    print("\nThe ConfigManager provides:")
    print("- JSON configuration loading and validation")
    print("- Environment-specific configuration management")
    print("- Automatic backup creation")
    print("- Configuration merging and templating")
    print("- Schema validation with custom rules")


if __name__ == "__main__":
    main()
