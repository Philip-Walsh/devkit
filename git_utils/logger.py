import logging
from typing import Dict, Any
from .config import ConfigManager

class GitLogger:
    """Custom logger for Git utilities"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize logger
        
        Args:
            config: Configuration dictionary. If None, uses default config.
        """
        self.config_manager = ConfigManager()
        self.config = config or self.config_manager.get_config()
        self._setup_logger()
        
    def _setup_logger(self) -> None:
        """Setup logging configuration"""
        logging.basicConfig(
            level=self.config['logging']['level'],
            format=self.config['logging']['format'],
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger('git-utils')
        
    def get_logger(self) -> logging.Logger:
        """Get configured logger instance"""
        return self.logger
        
    def log(self, level: str, message: str, **kwargs) -> None:
        """Log a message at the specified level
        
        Args:
            level: Logging level (e.g., 'info', 'warning', 'error')
            message: Message to log
            kwargs: Additional arguments for the log message
        """
        method = getattr(self.logger, level.lower())
        method(message, **kwargs)
        
    def error(self, message: str, **kwargs) -> None:
        """Log an error message"""
        self.log('error', message, **kwargs)
        
    def warning(self, message: str, **kwargs) -> None:
        """Log a warning message"""
        self.log('warning', message, **kwargs)
        
    def info(self, message: str, **kwargs) -> None:
        """Log an info message"""
        self.log('info', message, **kwargs)
        
    def debug(self, message: str, **kwargs) -> None:
        """Log a debug message"""
        self.log('debug', message, **kwargs)
