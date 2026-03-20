#!/usr/bin/env python3
"""
Conversation Logger for Week Report System

This script handles:
- GUID session management
- Message compression
- Response summarization
- Conversation recording to Git
"""

import os
import uuid
import json
import logging
import re
from datetime import datetime
from typing import Optional, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SessionManager:
    """Manages conversation session GUIDs and start dates."""

    SESSION_FILE = "/tmp/week_report_session.txt"
    SESSION_DATE_FILE = "/tmp/week_report_session_date.txt"

    @classmethod
    def get_or_create_guid(cls) -> str:
        """Get existing session GUID or create a new one."""
        # Check if session file exists and is recent (within 24 hours)
        if os.path.exists(cls.SESSION_FILE):
            try:
                file_time = os.path.getmtime(cls.SESSION_FILE)
                if (datetime.now().timestamp() - file_time) < 86400:  # 24 hours
                    with open(cls.SESSION_FILE, 'r') as f:
                        return f.read().strip()
            except Exception as e:
                logger.warning(f"Failed to read session file: {e}")

        # Create new GUID (8 characters)
        guid = uuid.uuid4().hex[:8]
        cls.save_guid(guid)
        return guid

    @classmethod
    def get_or_create_start_date(cls) -> str:
        """Get session start date (YYYYMMDD) for filename prefix."""
        if os.path.exists(cls.SESSION_DATE_FILE):
            try:
                file_time = os.path.getmtime(cls.SESSION_DATE_FILE)
                if (datetime.now().timestamp() - file_time) < 86400:
                    with open(cls.SESSION_DATE_FILE, 'r') as f:
                        return f.read().strip()
            except Exception:
                pass
        today = datetime.now().strftime("%Y%m%d")
        try:
            with open(cls.SESSION_DATE_FILE, 'w') as f:
                f.write(today)
        except Exception as e:
            logger.warning(f"Failed to save session date file: {e}")
        return today

    @classmethod
    def save_guid(cls, guid: str):
        """Save GUID to session file."""
        try:
            with open(cls.SESSION_FILE, 'w') as f:
                f.write(guid)
        except Exception as e:
            logger.warning(f"Failed to save session file: {e}")

    @classmethod
    def reset(cls):
        """Reset session (start new conversation)."""
        for f in [cls.SESSION_FILE, cls.SESSION_DATE_FILE]:
            if os.path.exists(f):
                os.remove(f)


class MessageCompressor:
    """Compresses long messages to key points."""

    MAX_LENGTH = 500
    SKIP_KEYWORDS = [
        'password', 'secret', 'api key', 'token', 'credential',
        'personal', 'private', 'confidential',
        "don't record", "skip logging", "off record"
    ]

    @classmethod
    def should_skip(cls, message: str) -> bool:
        """Check if message should be skipped for privacy."""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in cls.SKIP_KEYWORDS)

    @classmethod
    def compress(cls, message: str) -> str:
        """
        Compress message if too long.

        For messages > 500 chars, extract key points:
        - Main question/request
        - Important context
        - Specific requirements
        """
        if len(message) <= cls.MAX_LENGTH:
            return message

        # Simple compression: extract sentences with key indicators
        sentences = re.split(r'[.!?。!?]', message)

        key_sentences = []
        indicators = ['?', '？', '需要', '要求', '请', '帮我', '如何', '怎么',
                      'what', 'how', 'why', 'need', 'please', 'help']

        for sentence in sentences:
            if any(ind in sentence.lower() for ind in indicators):
                key_sentences.append(sentence.strip())

        compressed = '. '.join(key_sentences[:5])  # Max 5 key sentences

        if len(compressed) > cls.MAX_LENGTH:
            compressed = compressed[:cls.MAX_LENGTH - 3] + "..."

        return compressed if compressed else message[:cls.MAX_LENGTH - 3] + "..."


class ResponseSummarizer:
    """Summarizes AI responses to 2-3 sentences."""

    MAX_SENTENCES = 3

    @classmethod
    def summarize(cls, response: str) -> str:
        """
        Summarize response to key outcomes.

        Focus on:
        - Main outcomes
        - Solutions provided
        - Key decisions
        """
        # Split into sentences
        sentences = re.split(r'[.!?。!?]', response)

        # Filter out empty and code blocks
        filtered = []
        in_code_block = False

        for sentence in sentences:
            sentence = sentence.strip()

            # Track code blocks
            if '```' in sentence:
                in_code_block = not in_code_block
                continue

            if in_code_block:
                continue

            if sentence and len(sentence) > 10:
                filtered.append(sentence)

        # Take first N meaningful sentences
        summary_sentences = filtered[:cls.MAX_SENTENCES]
        summary = '. '.join(summary_sentences)

        if len(summary) > 300:
            summary = summary[:297] + "..."

        return summary if summary else "AI provided assistance."


class ConversationLogger:
    """Main class for logging conversations."""

    def __init__(self, git_manager):
        """
        Initialize conversation logger.

        Args:
            git_manager: GitManager instance for Git operations
        """
        self.git = git_manager
        self.buffer = []
        self.buffer_timestamp = None

    def get_week_path(self) -> str:
        """Get the path for current year/week directory."""
        now = datetime.now()
        year = now.year
        week = now.isocalendar()[1]
        return f"{year}/week{week:02d}"

    def format_entry(self, user_message: str, assistant_response: str) -> str:
        """Format a conversation entry."""
        now = datetime.now()
        timestamp = now.strftime("%H:%M:%S")
        week = now.isocalendar()
        week_str = f"{week[0]}-W{week[1]:02d}"

        # Compress and summarize
        compressed_user = MessageCompressor.compress(user_message)
        summarized_response = ResponseSummarizer.summarize(assistant_response)

        entry = f"""
## [{timestamp}] User
{compressed_user}

## [{timestamp}] Assistant
{summarized_response}
"""
        return entry

    def log_conversation(
        self,
        user_message: str,
        assistant_response: str,
        max_retries: int = 3
    ) -> bool:
        """
        Log a conversation exchange to Git.

        Args:
            user_message: Original user message
            assistant_response: AI response
            max_retries: Maximum retry attempts for Git operations

        Returns:
            True if successful, False otherwise
        """
        # Privacy check
        if MessageCompressor.should_skip(user_message):
            logger.info("Skipping conversation recording for privacy")
            return True

        try:
            # Get session GUID
            guid = SessionManager.get_or_create_guid()

            # Get week path
            week_path = self.get_week_path()

            # Format entry
            entry = self.format_entry(user_message, assistant_response)

            # Append to Git — filename: {YYYYMMDD}-{guid}.txt
            start_date = SessionManager.get_or_create_start_date()
            file_path = f"{week_path}/{start_date}-{guid}.txt"
            success = self.git.append_file(file_path, entry, max_retries)

            if success:
                logger.info(f"Conversation logged: {file_path}")
            else:
                logger.warning("Failed to log conversation after retries")

            return success

        except Exception as e:
            logger.error(f"Error logging conversation: {str(e)}")
            return False

    def get_week_conversations(self, year: int, week: int) -> list:
        """
        Get all conversations for a specific week.

        Args:
            year: Year (e.g., 2024)
            week: Week number (1-53)

        Returns:
            List of conversation dictionaries
        """
        week_path = f"{year}/week{week:02d}"

        # Pull latest
        self.git.pull()

        # List files
        files = self.git.list_files(week_path)

        conversations = []
        for file_path in files:
            content = self.git.read_file(file_path)
            if content:
                conversations.append({
                    'file': file_path,
                    'content': content,
                    'timestamp': os.path.getmtime(
                        os.path.join(self.git.repo_path, file_path)
                    )
                })

        # Sort by timestamp
        conversations.sort(key=lambda x: x['timestamp'])

        return conversations


def format_conversation_header(guid: str) -> str:
    """Create header for new conversation file."""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S")
    week = now.isocalendar()
    week_str = f"{week[0]}-W{week[1]:02d}"

    return f"""# Conversation: {guid}
# Date: {date_str}
# Week: {week_str}
"""


# CLI interface for testing
if __name__ == "__main__":
    import sys

    # Test compression
    long_message = """
    这是一条很长的测试消息，包含了大量的细节和背景信息。
    用户可能会在对话中提供很多上下文，但我们需要压缩这些信息。
    主要的问题是：如何处理多设备并发写入的问题？
    我们需要一个自动重试机制来处理这种情况。
    """ * 3

    print("Original length:", len(long_message))
    compressed = MessageCompressor.compress(long_message)
    print("Compressed length:", len(compressed))
    print("Compressed:", compressed)

    # Test summarization
    response = """
    这是一个AI回复的示例。我们提供了多设备并发写入的解决方案。
    主要使用Git的rebase机制来处理冲突。每次写入前先pull最新代码，
    然后追加内容，最后commit并push。如果push失败，就重试整个流程。
    这样可以确保数据的一致性和完整性。
    """

    summary = ResponseSummarizer.summarize(response)
    print("\nSummary:", summary)
