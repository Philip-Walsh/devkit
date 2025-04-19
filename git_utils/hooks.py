from git import Repo
from typing import Callable, Optional
import os
from .config import ConfigManager
from .logger import GitLogger

class HookManager:
    def __init__(self, repo_path: str = '.', config: Optional[dict] = None):
        """Initialize hook manager
        
        Args:
            repo_path: Path to git repository
            config: Configuration dictionary
        """
        self.repo = Repo(repo_path)
        self.config_manager = ConfigManager(config)
        self.logger = GitLogger(config).get_logger()
        self.hooks_dir = self.repo.git_dir / 'hooks'
        
    def install_hook(self, hook_name: str, hook_content: str) -> None:
        """Install a git hook
        
        Args:
            hook_name: Name of the hook (e.g., 'pre-commit', 'pre-push')
            hook_content: Content of the hook script
            
        Raises:
            ValueError: If hook is not enabled in configuration
        """
        if not self.config_manager.is_hook_enabled(hook_name):
            raise ValueError(f"Hook '{hook_name}' is disabled in configuration")
            
        hook_path = self.hooks_dir / hook_name
        try:
            with open(hook_path, 'w') as f:
                f.write(hook_content)
            hook_path.chmod(0o755)
            self.logger.info(f"Successfully installed {hook_name} hook")
        except Exception as e:
            self.logger.error(f"Error installing hook: {str(e)}")
            raise
            
    def add_pre_commit_hook(self, validation_func: Callable) -> None:
        """Add pre-commit hook for validation
        
        Args:
            validation_func: Function to validate commit
        """
        if not self.config_manager.is_hook_enabled('pre-commit'):
            self.logger.warning("Pre-commit hook is disabled in configuration")
            return
            
        hook_content = f"""#!/bin/sh
python -c 'from git_utils.hooks import HookManager; HookManager().validate_commit()'
"""
        self.install_hook('pre-commit', hook_content)
        
    def add_pre_push_hook(self, validation_func: Callable) -> None:
        """Add pre-push hook for validation
        
        Args:
            validation_func: Function to validate push
        """
        if not self.config_manager.is_hook_enabled('pre-push'):
            self.logger.warning("Pre-push hook is disabled in configuration")
            return
            
        hook_content = f"""#!/bin/sh
python -c 'from git_utils.hooks import HookManager; HookManager().validate_push()'
"""
        self.install_hook('pre-push', hook_content)
        
    def validate_commit(self) -> None:
        """Validate commit before commit"""
        # Implement commit validation logic
        pass
        
    def validate_push(self) -> None:
        """Validate push before push"""
        # Implement push validation logic
        pass
        
    def remove_hook(self, hook_name: str) -> None:
        """Remove a git hook
        
        Args:
            hook_name: Name of the hook to remove
        """
        hook_path = self.hooks_dir / hook_name
        if hook_path.exists():
            try:
                hook_path.unlink()
                self.logger.info(f"Successfully removed {hook_name} hook")
            except Exception as e:
                self.logger.error(f"Error removing hook: {str(e)}")
                raise
