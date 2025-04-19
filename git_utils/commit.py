from git import Repo
from typing import Optional, List
from .commit_validator import CommitValidator
from .logger import GitLogger

class CommitManager:
    def __init__(self, repo_path: str = '.', config: Optional[dict] = None):
        """Initialize commit manager
        
        Args:
            repo_path: Path to git repository
            config: Configuration dictionary
        """
        self.repo = Repo(repo_path)
        self.validator = CommitValidator(config)
        self.logger = GitLogger(config).get_logger()
        
    def validate_message(self, message: str) -> bool:
        """Validate commit message
        
        Args:
            message: Commit message to validate
            
        Returns:
            bool: True if message is valid, False otherwise
        """
        if not self.validator.validate_message(message):
            errors = self.validator.get_validation_errors(message)
            for error in errors:
                self.logger.error(error)
            return False
        return True
        
    def create_commit(self, message: str, files: Optional[List[str]] = None) -> None:
        """Create a new commit
        
        Args:
            message: Commit message
            files: List of files to commit
            
        Raises:
            ValueError: If commit message is invalid
        """
        try:
            if not self.validate_message(message):
                raise ValueError("Invalid commit message")
                
            if files:
                self.repo.git.add(files)
            else:
                self.repo.git.add('.')
                
            self.repo.git.commit('-m', message)
            self.logger.info(f"Successfully created commit: {message}")
            
        except Exception as e:
            self.logger.error(f"Error creating commit: {str(e)}")
            raise
            
    def get_commit_history(self, limit: int = 10) -> List[dict]:
        """Get recent commit history
        
        Args:
            limit: Maximum number of commits to return
            
        Returns:
            List of commit information dictionaries
        """
        commits = []
        for commit in self.repo.iter_commits(max_count=limit):
            commits.append({
                'sha': commit.hexsha,
                'message': commit.message,
                'author': commit.author.name,
                'date': commit.committed_datetime
            })
        return commits
        
    def revert_commit(self, commit: str) -> None:
        """Revert a specific commit
        
        Args:
            commit: Commit hash to revert
            
        Raises:
            ValueError: If commit hash is invalid
        """
        try:
            self.repo.git.revert(commit)
            self.logger.info(f"Successfully reverted commit: {commit}")
        except Exception as e:
            self.logger.error(f"Error reverting commit: {str(e)}")
            raise
