from git import Repo
from typing import List, Optional
from .config import ConfigManager
from .logger import GitLogger

class GitUtils:
    def __init__(self, repo_path: str = '.', config: Optional[dict] = None):
        """Initialize Git utilities
        
        Args:
            repo_path: Path to git repository
            config: Configuration dictionary
        """
        self.repo = Repo(repo_path)
        self.config_manager = ConfigManager(config)
        self.logger = GitLogger(config).get_logger()
        
    def get_current_branch(self) -> str:
        """Get current branch name
        
        Returns:
            str: Current branch name
        """
        try:
            branch = self.repo.active_branch.name
            self.logger.debug(f"Current branch: {branch}")
            return branch
        except Exception as e:
            self.logger.error(f"Error getting current branch: {str(e)}")
            raise
            
    def is_clean_working_directory(self) -> bool:
        """Check if working directory is clean
        
        Returns:
            bool: True if clean, False otherwise
        """
        try:
            is_clean = not self.repo.is_dirty()
            self.logger.debug(f"Working directory is {'clean' if is_clean else 'dirty'}")
            return is_clean
        except Exception as e:
            self.logger.error(f"Error checking working directory: {str(e)}")
            raise
            
    def get_untracked_files(self) -> List[str]:
        """Get list of untracked files
        
        Returns:
            List[str]: List of untracked files
        """
        try:
            untracked = self.repo.untracked_files
            self.logger.debug(f"Found {len(untracked)} untracked files")
            return untracked
        except Exception as e:
            self.logger.error(f"Error getting untracked files: {str(e)}")
            raise
            
    def get_remote_branches(self) -> List[str]:
        """Get list of remote branches
        
        Returns:
            List[str]: List of remote branch names
        """
        try:
            remote_branches = []
            for ref in self.repo.remote().refs:
                remote_branches.append(ref.name)
            self.logger.debug(f"Found {len(remote_branches)} remote branches")
            return remote_branches
        except Exception as e:
            self.logger.error(f"Error getting remote branches: {str(e)}")
            raise
            
    def get_local_branches(self) -> List[str]:
        """Get list of local branches
        
        Returns:
            List[str]: List of local branch names
        """
        try:
            local_branches = [b.name for b in self.repo.branches]
            self.logger.debug(f"Found {len(local_branches)} local branches")
            return local_branches
        except Exception as e:
            self.logger.error(f"Error getting local branches: {str(e)}")
            raise
            
    def get_status(self) -> dict:
        """Get repository status
        
        Returns:
            dict: Repository status information
        """
        try:
            status = {
                'branch': self.get_current_branch(),
                'is_clean': self.is_clean_working_directory(),
                'untracked_files': self.get_untracked_files(),
                'local_branches': self.get_local_branches(),
                'remote_branches': self.get_remote_branches()
            }
            self.logger.debug("Successfully got repository status")
            return status
        except Exception as e:
            self.logger.error(f"Error getting repository status: {str(e)}")
            raise
