# Conversation Tracking

How conversations are recorded to the Git repository after every AI response.

## Repository Structure

```
week-reports/
├── 2024/
│   ├── week01/
│   │   ├── 20240101-a1b2c3d4.txt    # Session started Jan 1
│   │   ├── 20240103-e5f6g7h8.txt    # Session started Jan 3
│   │   └── 20240105-i9j0k1l2.txt
│   ├── week02/
│   │   └── ...
│   └── ...
├── 2025/
│   └── ...
└── reports/
    ├── 2024_week01.md
    └── ...
```

## File Naming Convention

```
{YYYYMMDD}-{guid}.txt
```

- **Date prefix**: date the session started (`20241220`)
- **GUID**: 8-character hex unique identifier (`a1b2c3d4`)
- **One file per session**: all exchanges within the same AI session append to the same file
- Example: `20241220-a1b2c3d4.txt`

This naming makes files chronologically sortable while keeping each session's history together.

## Conversation File Format

```txt
# Conversation: a1b2c3d4
# Date: 2024-12-20 14:30:15
# Week: 2024-W51

## [14:30:15] User
Original user message or compressed summary (≤500 chars)...

## [14:30:45] Assistant
Brief summary of AI response (2-3 sentences)...

## [14:35:22] User
Follow-up question...

## [14:35:55] Assistant
Summary of response...

--- End of Session ---
Total exchanges: 4
```

---

## Recording Process

### Step 1: Get or Create Session GUID

```python
import uuid, os, datetime

SESSION_FILE = "/tmp/week_report_session.txt"

def get_session_guid():
    if os.path.exists(SESSION_FILE):
        return open(SESSION_FILE).read().strip()
    guid = uuid.uuid4().hex[:8]
    open(SESSION_FILE, 'w').write(guid)
    return guid

def get_session_start_date():
    """Return the date when the session was first created (for filename prefix)."""
    date_file = "/tmp/week_report_session_date.txt"
    if os.path.exists(date_file):
        return open(date_file).read().strip()
    today = datetime.datetime.now().strftime("%Y%m%d")
    open(date_file, 'w').write(today)
    return today
```

### Step 2: Compute Year and Week Path

```python
from datetime import datetime

def get_week_path():
    now = datetime.now()
    year = now.year
    week = now.isocalendar()[1]   # ISO week number (1–53)
    return f"{year}/week{week:02d}"
```

### Step 3: Compress User Message

If the message exceeds 500 characters, summarize it to key points. Focus on: main question, important context, specific requirements. Discard pleasantries and repetition.

```python
def compress_message(message: str, max_len: int = 500) -> str:
    if len(message) <= max_len:
        return message
    # Use AI summarization:
    # "Summarize the following message into key points in ≤500 characters.
    #  Keep: main question, important context, specific requirements.
    #  Message: {message}"
    return compressed
```

### Step 4: Summarize AI Response

Condense your own response to 2-3 sentences. Focus on: main outcome, solution provided, key decision made.

### Step 5: Format Entry

```python
from datetime import datetime

def format_entry(guid: str, user_msg: str, assistant_summary: str, is_first: bool) -> str:
    now = datetime.now()
    ts = now.strftime("%H:%M:%S")
    week_label = f"{now.year}-W{now.isocalendar()[1]:02d}"

    lines = []
    if is_first:
        lines += [
            f"# Conversation: {guid}",
            f"# Date: {now.strftime('%Y-%m-%d %H:%M:%S')}",
            f"# Week: {week_label}",
            "",
        ]
    lines += [
        f"## [{ts}] User",
        user_msg,
        "",
        f"## [{ts}] Assistant",
        assistant_summary,
        "",
    ]
    return "\n".join(lines)
```

### Step 6: Append to Git

```python
from scripts.git_operations import create_git_manager

def record_conversation(user_msg: str, assistant_response: str):
    try:
        guid = get_session_guid()
        start_date = get_session_start_date()
        week_path = get_week_path()
        file_name = f"{start_date}-{guid}.txt"
        file_path = f"{week_path}/{file_name}"

        # Check privacy
        if should_skip_recording(user_msg):
            return

        # Compress/summarize
        compressed_user = compress_message(user_msg)
        summary_ai = summarize_response(assistant_response)

        # Check if file already exists
        git = create_git_manager()
        if not git:
            return

        is_first = not os.path.exists(
            os.path.join(git.repo_path, file_path)
        )

        entry = format_entry(guid, compressed_user, summary_ai, is_first)

        git.pull()
        git.append_to_file(file_path, entry)
        git.commit_and_push(f"Log conversation {guid} [{week_path}]")

    except Exception as e:
        # Never interrupt the user — swallow all errors silently
        pass
```

---

## Privacy Filter

Skip recording for messages containing:

```python
SKIP_KEYWORDS = [
    'password', 'passwd', 'secret', 'api key', 'apikey',
    'personal token', 'credential', 'private key',
    'don\'t record', "don't log", 'skip logging', 'off record', 'off the record',
    '不要记录', '跳过记录', '私密',
]

def should_skip_recording(message: str) -> bool:
    msg_lower = message.lower()
    return any(kw in msg_lower for kw in SKIP_KEYWORDS)
```

---

## Multi-Device Conflict Handling

When two devices push simultaneously:

```
T1  Device A: pull         Device B: pull        → both up to date
T2  Device A: append       Device B: append      → local changes
T3  Device A: push ✓       Device B: push ✗      → conflict!
T4                         Device B: pull+merge  → resolved
T5                         Device B: push ✓      → done
```

The retry logic in `scripts/git_operations.py` handles this automatically (up to 3 retries with pull-rebase between attempts).
