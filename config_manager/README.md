# Configuration Manager

A simple, practical JSON configuration manager for Python applications.

## Features

- ✅ Load and validate JSON configurations
- ✅ Environment-specific configs (dev/staging/prod)
- ✅ Automatic backups before changes
- ✅ Configuration templates
- ✅ Deep merge configurations
- ✅ Schema validation

## Quick Start

```python
from config_manager import ConfigManager

# Initialize
config = ConfigManager("my_configs")

# Load configuration
app_config = config.load_config("app.json")

# Get environment-specific config
dev_config = config.get_environment_config("app.json", "dev")
```

## Installation

Just copy `config_manager.py` to your project. Uses only Python built-ins.

## Usage Examples

### Basic Configuration

```python
# Create a basic config
config_data = {
    "app_name": "MyApp",
    "version": "1.0.0",
    "debug": False,
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "myapp_db"
    }
}

# Save it
config.save_config(config_data, "app.json")

# Load it back
loaded_config = config.load_config("app.json")
```

### Environment-Specific Configs

Create base config: `app.json`
```json
{
  "app_name": "MyApp",
  "debug": false,
  "database": {
    "host": "localhost",
    "name": "myapp_db"
  }
}
```

Create dev overrides: `app.dev.json`
```json
{
  "debug": true,
  "database": {
    "name": "myapp_dev_db"
  }
}
```

```python
# Automatically merges base + environment configs
dev_config = config.get_environment_config("app.json", "dev")
# Result: debug=True, database.name="myapp_dev_db"
```

### Configuration Validation

```python
# This will validate required fields and types
try:
    config.load_config("app.json", validate=True)
    print("✅ Configuration is valid")
except ConfigurationError as e:
    print(f"❌ Invalid config: {e}")
```

### Backups

```python
# Automatic backup before saving
config.save_config(new_config, "app.json", create_backup=True)

# Manual backup
backup_path = config.backup_config("app.json")

# List all backups
backups = config.list_backups()
```

### Templates

```python
# Create a template
template = {
    "app_name": "{{APP_NAME}}",
    "database": {
        "host": "{{DB_HOST}}",
        "user": "{{DB_USER}}"
    }
}

config.create_template("webapp", template)
```


