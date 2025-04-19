import click
from git_utils import CommitManager, HookManager, GitUtils

class GitUtilsCLI:
    def __init__(self, repo_path='.'):
        self.repo_path = repo_path
        self.commit_mgr = CommitManager(repo_path)
        self.hook_mgr = HookManager(repo_path)
        self.git_utils = GitUtils(repo_path)

@click.group()
def cli():
    """Git Utilities CLI"""

@cli.command()
@click.argument('message')
@click.option('--files', '-f', multiple=True, help='Specific files to commit')
def commit(message, files):
    """Create a new commit"""
    try:
        cli = GitUtilsCLI()
        cli.commit_mgr.create_commit(message, files)
        click.echo(f"Successfully created commit: {message}")
    except Exception as e:
        click.echo(f"Error creating commit: {str(e)}", err=True)

@cli.command()
@click.argument('hook_name')
@click.argument('hook_content', type=click.File('r'))
def install_hook(hook_name, hook_content):
    """Install a git hook"""
    try:
        cli = GitUtilsCLI()
        cli.hook_mgr.install_hook(hook_name, hook_content.read())
        click.echo(f"Successfully installed {hook_name} hook")
    except Exception as e:
        click.echo(f"Error installing hook: {str(e)}", err=True)

@cli.command()
def status():
    """Get repository status"""
    try:
        cli = GitUtilsCLI()
        click.echo(f"Current Branch: {cli.git_utils.get_current_branch()}")
        if cli.git_utils.is_clean_working_directory():
            click.echo("Working directory is clean")
        else:
            click.echo("Working directory has changes")
            click.echo("Untracked files:")
            for file in cli.git_utils.get_untracked_files():
                click.echo(f"  {file}")
    except Exception as e:
        click.echo(f"Error getting status: {str(e)}", err=True)

if __name__ == '__main__':
    cli()
