import pytest
from git_utils.commit import CommitManager
from git import Repo

def test_commit_message_validation():
    """Test commit message validation"""
    manager = CommitManager()
    
    # Valid commit messages
    assert manager.validate_message("feat: add new feature") == True
    assert manager.validate_message("fix: resolve bug") == True
    assert manager.validate_message("docs: update documentation") == True
    
    # Invalid commit messages
    assert manager.validate_message("invalid message") == False
    assert manager.validate_message("too long message that exceeds the recommended length") == False
    assert manager.validate_message("") == False

def test_create_commit(tmp_path):
    """Test creating a commit"""
    # Create a temporary git repository
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    repo = Repo.init(str(repo_path))
    
    # Create a test file
    test_file = repo_path / "test.txt"
    test_file.write_text("test content")
    
    # Create commit manager
    manager = CommitManager(str(repo_path))
    
    # Create commit
    manager.create_commit("feat: add test file", [str(test_file)])
    
    # Verify commit was created
    assert len(list(repo.iter_commits())) == 1
    assert repo.head.commit.message == "feat: add test file\n"
