import pytest
from git_utils.hooks import HookManager
from git import Repo
import os

def test_install_hook(tmp_path):
    """Test installing a git hook"""
    # Create a temporary git repository
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    repo = Repo.init(str(repo_path))
    
    # Create hook manager
    manager = HookManager(str(repo_path))
    
    # Test installing a hook
    hook_content = "#!/bin/sh\necho 'Hook executed'"
    manager.install_hook("pre-commit", hook_content)
    
    # Verify hook was installed
    hook_path = repo_path / ".git" / "hooks" / "pre-commit"
    assert hook_path.exists()
    assert hook_path.read_text() == hook_content
    assert os.access(hook_path, os.X_OK)  # Verify executable

def test_add_pre_commit_hook(tmp_path):
    """Test adding a pre-commit hook"""
    # Create a temporary git repository
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    repo = Repo.init(str(repo_path))
    
    # Create hook manager
    manager = HookManager(str(repo_path))
    
    # Test adding pre-commit hook
    manager.add_pre_commit_hook(lambda: True)
    
    # Verify hook was installed
    hook_path = repo_path / ".git" / "hooks" / "pre-commit"
    assert hook_path.exists()
    assert os.access(hook_path, os.X_OK)
