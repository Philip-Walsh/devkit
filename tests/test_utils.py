import pytest
from git_utils.utils import GitUtils
from git import Repo

def test_get_current_branch(tmp_path):
    """Test getting current branch"""
    # Create a temporary git repository
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    repo = Repo.init(str(repo_path))
    
    # Create git utils
    utils = GitUtils(str(repo_path))
    
    # Test getting current branch
    assert utils.get_current_branch() == "master"  # Default branch name

def test_is_clean_working_directory(tmp_path):
    """Test checking if working directory is clean"""
    # Create a temporary git repository
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    repo = Repo.init(str(repo_path))
    
    # Create git utils
    utils = GitUtils(str(repo_path))
    
    # Test clean working directory
    assert utils.is_clean_working_directory() == True
    
    # Create untracked file
    test_file = repo_path / "test.txt"
    test_file.write_text("test content")
    
    # Test dirty working directory
    assert utils.is_clean_working_directory() == False

def test_get_untracked_files(tmp_path):
    """Test getting untracked files"""
    # Create a temporary git repository
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    repo = Repo.init(str(repo_path))
    
    # Create git utils
    utils = GitUtils(str(repo_path))
    
    # Create untracked files
    file1 = repo_path / "file1.txt"
    file2 = repo_path / "file2.txt"
    file1.write_text("content 1")
    file2.write_text("content 2")
    
    # Test getting untracked files
    untracked = utils.get_untracked_files()
    assert len(untracked) == 2
    assert "file1.txt" in untracked
    assert "file2.txt" in untracked
