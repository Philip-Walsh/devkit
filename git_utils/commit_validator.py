from typing import Dict, Any
import re
from .config import ConfigManager

class CommitValidator:
    """Validate commit messages against configured rules"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize commit validator
        
        Args:
            config: Configuration dictionary. If None, uses default config.
        """
        self.config_manager = ConfigManager()
        self.config = config or self.config_manager.get_config()
        
    def validate_message(self, message: str) -> bool:
        """Validate commit message against all rules
        
        Args:
            message: Commit message to validate
            
        Returns:
            bool: True if message is valid, False otherwise
        """
        if not message:
            return False
            
        # Check length
        if len(message) > self.config['commit']['rules']['max_length']:
            return False
            
        # Check format based on type
        message_type = message.split(':')[0].strip()
        if message_type not in self.config['commit']['rules']['allowed_types']:
            return False
            
        # Validate based on format
        if 'conventional' in self.config['commit']['formats']:
            return self._validate_conventional(message)
        elif 'semantic' in self.config['commit']['formats']:
            return self._validate_semantic(message)
        return True
        
    def _validate_conventional(self, message: str) -> bool:
        """Validate conventional commit format
        
        Args:
            message: Commit message to validate
            
        Returns:
            bool: True if message is valid conventional commit, False otherwise
        """
        pattern = r'^(feat|fix|docs|style|refactor|test|chore)\(([^)]+)\): .+$'
        return bool(re.match(pattern, message))
        
    def _validate_semantic(self, message: str) -> bool:
        """Validate semantic commit format
        
        Args:
            message: Commit message to validate
            
        Returns:
            bool: True if message is valid semantic commit, False otherwise
        """
        pattern = r'^(build|ci|docs|feat|fix|perf|refactor|style|test|chore)\(([^)]+)\): .+$'
        return bool(re.match(pattern, message))
        
    def get_validation_errors(self, message: str) -> list:
        """Get list of validation errors for a commit message
        
        Args:
            message: Commit message to validate
            
        Returns:
            list: List of validation errors
        """
        errors = []
        
        if not message:
            errors.append("Commit message cannot be empty")
            return errors
            
        # Check length
        if len(message) > self.config['commit']['rules']['max_length']:
            errors.append(f"Commit message exceeds maximum length of {self.config['commit']['rules']['max_length']} characters")
            
        # Check format based on type
        message_type = message.split(':')[0].strip()
        if message_type not in self.config['commit']['rules']['allowed_types']:
            errors.append(f"Invalid commit type '{message_type}'. Must be one of: {', '.join(self.config['commit']['rules']['allowed_types'])}")
            
        # Validate based on format
        if 'conventional' in self.config['commit']['formats']:
            if not self._validate_conventional(message):
                errors.append("Commit message does not follow conventional commit format")
        elif 'semantic' in self.config['commit']['formats']:
            if not self._validate_semantic(message):
                errors.append("Commit message does not follow semantic commit format")
                
        return errors
