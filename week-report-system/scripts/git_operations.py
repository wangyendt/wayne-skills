#!/usr/bin/env python3
"""
Git Operations for Week Report System

This script handles all Git-related operations including:
- Repository cloning and pulling
- Conflict resolution with automatic retry
- Conversation file management
"""

import os
import subprocess
import time
import logging
from typing import Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GitOperationError(Exception):
    """Custom exception for Git operation failures."""
    pass


class PushConflictError(GitOperationError):
    """Exception raised when push fails due to remote changes."""
    pass


class GitManager:
    """Manages Git operations for the week report system."""

    def __init__(
        self,
        username: str,
        token: str,
        repo: str,
        local_path: Optional[str] = None
    ):
        """
        Initialize Git manager.

        Args:
            username: GitHub username
            token: GitHub personal access token
            repo: Repository name in format "username/repo"
            local_path: Local path for repository (default: ~/.week-report-repo)
        """
        self.username = username
        self.token = token
        self.repo = repo
        self.repo_url = f"https://{username}:{token}@github.com/{repo}.git"
        self.local_path = local_path or os.path.expanduser("~/.week-report-repo")
        self.repo_path = os.path.join(self.local_path, repo.split('/')[-1])

    def _run_git_command(self, *args, retry_on_conflict: bool = False) -> tuple:
        """
        Run a git command and return (success, output, error).

        Args:
            *args: Git command arguments
            retry_on_conflict: Whether to handle conflicts automatically

        Returns:
            Tuple of (success: bool, stdout: str, stderr: str)
        """
        cmd = ['git'] + list(args)
        logger.debug(f"Running: git {' '.join(args)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()

                # Check for push conflict
                if 'non-fast-forward' in error_msg or 'fetch first' in error_msg:
                    if retry_on_conflict:
                        raise PushConflictError("Remote has new commits")
                    return False, result.stdout, error_msg

                logger.error(f"Git command failed: {error_msg}")
                return False, result.stdout, error_msg

            return True, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            logger.error("Git command timed out")
            return False, "", "Command timed out"
        except Exception as e:
            logger.error(f"Git command exception: {str(e)}")
            return False, "", str(e)

    def is_repo_initialized(self) -> bool:
        """Check if repository is already cloned."""
        return os.path.exists(os.path.join(self.repo_path, '.git'))

    def clone(self) -> bool:
        """Clone the repository."""
        try:
            os.makedirs(self.local_path, exist_ok=True)

            cmd = ['git', 'clone', self.repo_url, self.repo_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode != 0:
                # Check if repo is empty - that's OK
                if 'empty repository' in result.stderr or 'repository is empty' in result.stderr.lower():
                    logger.info("Repository is empty, will initialize")
                    os.makedirs(self.repo_path, exist_ok=True)
                    subprocess.run(['git', 'init'], cwd=self.repo_path, capture_output=True)
                    subprocess.run(['git', 'remote', 'add', 'origin', self.repo_url],
                                   cwd=self.repo_path, capture_output=True)
                    return True
                logger.error(f"Clone failed: {result.stderr}")
                return False

            logger.info(f"Repository cloned to {self.repo_path}")
            return True

        except Exception as e:
            logger.error(f"Clone exception: {str(e)}")
            return False

    def pull(self, force: bool = False) -> bool:
        """
        Pull latest changes from remote.

        Args:
            force: If True, reset local changes before pulling

        Returns:
            True if successful, False otherwise
        """
        if not self.is_repo_initialized():
            return self.clone()

        try:
            if force:
                # Reset any local changes
                self._run_git_command('reset', '--hard', 'HEAD')
                self._run_git_command('clean', '-fd')

            # Fetch and merge
            success, _, error = self._run_git_command('pull', '--rebase', 'origin', 'main')

            if not success:
                # Try 'master' branch if 'main' fails
                success, _, _ = self._run_git_command('pull', '--rebase', 'origin', 'master')

            return success

        except Exception as e:
            logger.error(f"Pull failed: {str(e)}")
            return False

    def push(self) -> bool:
        """Push changes to remote."""
        # Try main branch first, then master
        success, _, _ = self._run_git_command('push', 'origin', 'main')

        if not success:
            success, _, _ = self._run_git_command('push', 'origin', 'master')

        if not success:
            raise PushConflictError("Push failed - remote may have new commits")

        return True

    def commit_and_push(self, message: str, max_retries: int = 3) -> bool:
        """
        Commit and push changes with automatic retry on conflicts.

        Separates commit (done once) from push (retried on conflict).

        Args:
            message: Commit message
            max_retries: Maximum number of retry attempts for push

        Returns:
            True if successful, False otherwise
        """
        try:
            # Stage and commit once
            self._run_git_command('add', '-A')
            success, _, _ = self._run_git_command('commit', '-m', message)
            if not success:
                # Nothing to commit
                return True
        except Exception as e:
            logger.error(f"Commit failed: {str(e)}")
            return False

        # Push with retry on conflict
        for attempt in range(max_retries):
            try:
                self.push()
                logger.info(f"Successfully committed and pushed: {message}")
                return True

            except PushConflictError:
                if attempt < max_retries - 1:
                    logger.warning(f"Push conflict, retrying ({attempt + 1}/{max_retries})")
                    time.sleep(1)
                    self.pull()  # Rebase local commit on top of remote changes
                else:
                    logger.error("Max retries reached, giving up")
                    return False

            except Exception as e:
                logger.error(f"Push failed: {str(e)}")
                return False

        return False

    def append_to_file(self, file_path: str, content: str) -> bool:
        """
        Append content to a file in the repository.

        Args:
            file_path: Relative path from repo root
            content: Content to append

        Returns:
            True if successful
        """
        full_path = os.path.join(self.repo_path, file_path)

        # Create directory if needed
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Append content
        with open(full_path, 'a', encoding='utf-8') as f:
            f.write(content)

        return True

    def read_file(self, file_path: str) -> Optional[str]:
        """Read file content from repository."""
        full_path = os.path.join(self.repo_path, file_path)

        if not os.path.exists(full_path):
            return None

        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()

    def list_files(self, directory: str = "") -> list:
        """List all files in a directory."""
        full_path = os.path.join(self.repo_path, directory)

        if not os.path.exists(full_path):
            return []

        files = []
        for root, _, filenames in os.walk(full_path):
            for filename in filenames:
                if filename.endswith('.txt'):
                    rel_path = os.path.relpath(os.path.join(root, filename), self.repo_path)
                    files.append(rel_path)

        return files


def create_git_manager() -> Optional[GitManager]:
    """
    Create a GitManager instance from environment variables.

    Returns:
        GitManager if all env vars are set, None otherwise
    """
    username = os.environ.get('WEEK_REPORT_GIT_USERNAME')
    token = os.environ.get('WEEK_REPORT_GIT_PERSONAL_TOKEN')
    repo = os.environ.get('WEEK_REPORT_GIT_REPO')

    if not all([username, token, repo]):
        logger.warning("Missing environment variables for Git configuration")
        return None

    return GitManager(username, token, repo)


# CLI interface for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python git_operations.py <command> [args]")
        print("Commands: clone, pull, status")
        sys.exit(1)

    command = sys.argv[1]

    git = create_git_manager()
    if not git:
        print("Error: Please set environment variables first")
        sys.exit(1)

    if command == "clone":
        success = git.clone()
        print(f"Clone: {'Success' if success else 'Failed'}")

    elif command == "pull":
        success = git.pull()
        print(f"Pull: {'Success' if success else 'Failed'}")

    elif command == "status":
        if git.is_repo_initialized():
            print(f"Repository initialized at: {git.repo_path}")
            files = git.list_files()
            print(f"Files: {len(files)}")
        else:
            print("Repository not initialized")
