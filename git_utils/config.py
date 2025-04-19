import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manage configuration for Git utilities"""
    
    DEFAULT_CONFIG = {
        'commit': {
            'formats': ['conventional', 'semantic'],
            'rules': {
                'max_length': 100,
                'required_fields': ['type', 'scope', 'description'],
                'allowed_types': ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore']
            }
        },
        'hooks': {
            'enabled': True,
            'pre-commit': True,
            'pre-push': True,
            'pre-rebase': True
        },
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager
        
        Args:
            config_path: Path to configuration file. If None, looks for git-utils.yml in current directory.
        """
        self.config_path = config_path or Path('.').joinpath('git-utils.yml')
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or return default"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                return self._validate_config(config)
            return self.DEFAULT_CONFIG
        except Exception as e:
            logger.warning(f"Error loading config: {e}")
            return self.DEFAULT_CONFIG
            
    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration against default schema"""
        validated = {}
        for section, default in self.DEFAULT_CONFIG.items():
            if section in config:
                validated[section] = {**default, **config[section]}
            else:
                validated[section] = default
        return validated
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update configuration and save to file"""
        self.config.update(new_config)
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            
    def get_commit_formats(self) -> list:
        """Get supported commit message formats"""
        return self.config['commit']['formats']
    
    def get_commit_rules(self) -> Dict[str, Any]:
        """Get commit message validation rules"""
        return self.config['commit']['rules']
    
    def is_hook_enabled(self, hook_name: str) -> bool:
        """Check if a hook is enabled"""
        return self.config['hooks'].get(hook_name, False)
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.config['logging']
