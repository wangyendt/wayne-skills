---
name: pywayne-lark-bot
description: Feishu/Lark Bot API wrapper for full-featured Feishu bot interactions. Use when users need to send messages (text, image, audio, file, post, interactive, share), especially Markdown delivery via send_markdown_to_chat with card_v2/post routing, table fallback, and auto chunking; manage files (upload/download); query user/group info; reply to messages; forward/recall/update messages; add reactions; pin messages; manage chats (create, delete, update, members, admins); get message history; batch send; handle read receipts and urgent notifications.
---

# Pywayne Lark Bot - Full-Featured Feishu API Wrapper

## Overview

`LarkBot` is a comprehensive Feishu (Lark) application bot wrapper that provides complete bidirectional interaction capabilities. It's designed for scenarios requiring **full message lifecycle management, chat administration, and complex interactive features**.

**Key Capabilities**:
- Send all message types (text, image, audio, video, file, post, interactive cards)
- Reply, forward, recall, update messages
- Reactions, pins, read receipts, urgent notifications
- Chat management (create, delete, update, members, admins, announcements)
- File upload/download with message resource handling
- User and group information queries
- Batch messaging to users/departments
- **Recommended**: `send_markdown_to_chat` with auto-chunking and table fallback

**Companion Classes**:
- `TextContent`: Quick text formatting (@mentions, bold, italic, links)
- `PostContent`: Rich text post builder with Markdown table handling
- `CardContentV2`: Schema 2.0 interactive card builder
- `LarkBotListener`: Event listener for incoming messages (separate skill)

## Installation

```bash
pip install pywayne lark-oapi
```

## Quick Start

```python
from pywayne.lark_bot import LarkBot

# Initialize bot
bot = LarkBot(
    app_id="cli_xxxxxxxxxxxx",
    app_secret="your_app_secret"
)

# Send text to user
bot.send_text_to_user("ou_xxxxxxxx", "Hello from LarkBot!")

# Send text to chat group
bot.send_text_to_chat("oc_xxxxxxxx", "Hello, everyone!")
```

## LarkBot Class

### Constructor

```python
bot = LarkBot(
    app_id: str,        # Feishu application ID
    app_secret: str     # Feishu application secret
)
```

**Instance Attributes**:
- `client`: Underlying `lark.Client` for advanced usage
- All methods return `Dict` with API response data

## Helper Classes

### TextContent - Quick Text Formatting

Static helper for creating formatted text patterns used in text messages.

**Available Methods**:

```python
from pywayne.lark_bot import TextContent

# @mentions
at_all = TextContent.make_at_all_pattern()
at_user = TextContent.make_at_someone_pattern("ou_xxxx", "John", "open_id")

# Text styles
bold = TextContent.make_bold_pattern("Bold text")
italic = TextContent.make_italian_pattern("Italic text")
underline = TextContent.make_underline_pattern("Underlined text")
strikethrough = TextContent.make_delete_line_pattern("Strike text")

# Links
link = TextContent.make_url_pattern("https://example.com", "Click here")
```

**Example: Formatted Notification**:

```python
from pywayne.lark_bot import LarkBot, TextContent

bot = LarkBot(app_id="cli_xxx", app_secret="sec_xxx")

message = (
    TextContent.make_at_someone_pattern("ou_xxxx", "Wayne", "open_id")
    + " "
    + TextContent.make_bold_pattern("Deployment completed")
    + " - "
    + TextContent.make_url_pattern("https://jenkins.example.com", "View build")
)

bot.send_text_to_chat("oc_xxxx", message)
```

### PostContent - Rich Text Post Builder

Builder for complex structured rich text messages supporting text, links, @mentions, images, code blocks, and Markdown content.

**Constructor**:

```python
from pywayne.lark_bot import PostContent

post = PostContent(title="Post Title")
```

**Content Creation Methods**:

```python
# Text with optional styles
text = post.make_text_content("Text", styles=["bold", "underline", "lineThrough", "italic"])

# Hyperlink
link = post.make_link_content("Display text", "https://example.com")

# @mention
at = post.make_at_content("ou_xxxx", styles=["bold"])

# Image
img = post.make_image_content("img_key")

# Media (video/audio with thumbnail)
media = post.make_media_content(file_key="file_xxx", image_key="thumb_xxx")

# Emoji (Feishu emoji codes like "OK", "THUMBSUP", "HEART")
emoji = post.make_emoji_content("THUMBSUP")

# Horizontal rule
hr = post.make_hr_content()

# Code block
code = post.make_code_block_content(language="python", text='print("hello")')

# Markdown
md = post.make_markdown_content("**Bold** and *italic*")
```

**Adding Content**:

```python
# Add to current line
post.add_content_in_line(content_dict)
post.add_contents_in_line([content1, content2])  # Multiple elements in same line

# Add to new line
post.add_content_in_new_line(content_dict)
post.add_contents_in_new_line([content1, content2])
```

**Recommended: Add Markdown Directly**:

```python
md_text = """
## Section Title

- Item 1
- Item 2

| Column A | Column B |
| -------- | -------- |
| Data 1   | Data 2   |
"""

# Auto-chunk and handle tables
post.add_markdown(
    md_text,
    table_as="code_block",      # "code_block" or "md"
    max_chunk_bytes=8000,       # Max bytes per chunk
    mono_max_col_width=40       # Max column width for code_block mode
)

# Send
bot.send_post_to_chat("oc_xxx", post.get_content())
```

**Complete Example**:

```python
from pywayne.lark_bot import LarkBot, PostContent

bot = LarkBot(app_id="cli_xxx", app_secret="sec_xxx")

# Build post
post = PostContent(title="Release Report")

# Line 1: Title
post.add_content_in_new_line(
    post.make_text_content("Version 1.2.0 Released", styles=["bold"])
)

# Line 2: @mention with emoji
post.add_contents_in_new_line([
    post.make_at_content("ou_xxx"),
    post.make_text_content(" "),
    post.make_emoji_content("OK")
])

# Line 3: Link
post.add_content_in_new_line(
    post.make_link_content("View release notes", "https://example.com/release/1.2.0")
)

# Line 4: Code block
post.add_content_in_new_line(
    post.make_code_block_content("bash", "deploy.sh --env prod --version 1.2.0")
)

# Send
bot.send_post_to_chat("oc_xxx", post.get_content())
```

### CardContentV2 - Schema 2.0 Interactive Card Builder

Lightweight builder for Feishu schema 2.0 interactive cards, ideal for announcements, reports, and status updates with Markdown content.

**Constructor**:

```python
from pywayne.lark_bot import CardContentV2

card = CardContentV2(
    title="Card Title",      # Optional header title
    template="blue"          # Header color: "blue", "wathet", "turquoise", "green", "yellow", "orange", "red", "carmine", "violet", "purple", "indigo", "grey"
)
```

**Methods**:

```python
# Add Markdown content (auto-chunks by bytes)
card.add_markdown(md_text: str, *, max_chunk_bytes: int = 18_000)

# Add horizontal divider
card.add_hr()

# Add image
card.add_image(img_key: str, *, size: str = "large", preview: bool = True)

# Get complete card JSON
card_json = card.get_card()
```

**Example: Daily Report Card**:

```python
from pywayne.lark_bot import LarkBot, CardContentV2

bot = LarkBot(app_id="cli_xxx", app_secret="sec_xxx")

# Build card
card = CardContentV2(title="Daily Report", template="blue")

card.add_markdown("""
# Today's Progress

- ✅ API integration completed
- ✅ Fixed 3 critical bugs
- 🔄 Code review in progress
- 📝 Documentation updated
""")

card.add_hr()

card.add_markdown("**Next Steps**: Deploy to staging environment")

# Send
bot.send_interactive_to_chat("oc_xxx", card.get_card())
```

## Core Messaging Methods

### Recommended Entry Point: send_markdown_to_chat

**The preferred high-level method for sending Markdown content** with automatic chunking, table handling, and dual routing (card_v2/post).

```python
responses = bot.send_markdown_to_chat(
    chat_id: str,
    md_text: str,
    *,
    title: str = "",
    prefer: str = "card_v2",              # "card_v2" or "post"
    table_fallback: str = "code_block",   # "code_block" or "md" (for post route)
    max_message_bytes: Optional[int] = None
) -> List[Dict]
```

**Parameters**:
- `chat_id`: Target chat ID
- `md_text`: Markdown content
- `title`: Message title
- `prefer`: Route preference:
  - `"card_v2"` (default): Send as schema 2.0 interactive card (supports most Markdown)
  - `"post"`: Send as rich text post (supports table fallback)
- `table_fallback`: How to render Markdown tables in post route:
  - `"code_block"`: Convert tables to fixed-width text blocks (stable, recommended)
  - `"md"`: Keep tables as Markdown (may have layout issues)
- `max_message_bytes`: Per-message byte limit (defaults: 18k for card_v2, 8k for post)

**Returns**: List of API response dicts for all sent chunks

**Example 1: Simple Markdown (Default card_v2)**:

```python
md = """
# Deployment Complete

- API: v1.2.3
- Frontend: v2.4.5
- Database: migrated

✅ All services healthy
"""

bot.send_markdown_to_chat(
    "oc_xxx",
    md_text=md,
    title="Deployment Status"
)
```

**Example 2: Markdown with Tables (Post route with fallback)**:

```python
md = """
## Test Results

| Module   | Status | Coverage |
| -------- | ------ | -------- |
| Auth     | ✅     | 95%      |
| Payment  | ✅     | 87%      |
| API      | ⚠️     | 72%      |
"""

bot.send_markdown_to_chat(
    "oc_xxx",
    md_text=md,
    title="Test Report",
    prefer="post",                    # Use post for table support
    table_fallback="code_block"       # Convert table to fixed-width text
)
```

**Example 3: Long Markdown Auto-Chunking**:

```python
# Very long markdown content
long_md = "\n".join([f"## Section {i}\n\n" + "- " * 50 for i in range(50)])

# Automatically split into multiple messages
responses = bot.send_markdown_to_chat(
    "oc_xxx",
    md_text=long_md,
    title="Long Report",
    prefer="card_v2",
    max_message_bytes=10000  # Custom chunk size
)

print(f"Sent {len(responses)} message chunks")
```

**Why Use send_markdown_to_chat?**
- Handles large content automatically
- Tables render reliably with fallback
- Single API for both card and post routes
- No manual JSON construction
- Consistent chunking and encoding

### Text Messages

```python
# Send to user
bot.send_text_to_user(user_open_id: str, text: str = '') -> Dict

# Send to chat
bot.send_text_to_chat(chat_id: str, text: str = '') -> Dict
```

**Examples**:

```python
# Simple text
bot.send_text_to_user("ou_xxx", "Hello!")

# With formatting (use TextContent helpers)
from pywayne.lark_bot import TextContent

msg = (
    TextContent.make_at_all_pattern() + " "
    + TextContent.make_bold_pattern("Important")
    + ": System maintenance tonight at 23:00"
)
bot.send_text_to_chat("oc_xxx", msg)
```

### Image Messages

```python
# Upload image
image_key = bot.upload_image(image_path: str) -> str

# Send to user
bot.send_image_to_user(user_open_id: str, image_key: str) -> Dict

# Send to chat
bot.send_image_to_chat(chat_id: str, image_key: str) -> Dict

# Download image
bot.download_image(image_key: str, image_save_path: str) -> None
```

**Example**:

```python
# Upload and send
image_key = bot.upload_image("/tmp/report.png")
if image_key:
    bot.send_image_to_chat("oc_xxx", image_key)
```

### Audio Messages

```python
# Upload audio (typically .opus format)
audio_key = bot.upload_file(file_path: str, file_type: str = "opus") -> str

# Send to user
bot.send_audio_to_user(user_open_id: str, file_key: str) -> Dict

# Send to chat
bot.send_audio_to_chat(chat_id: str, file_key: str) -> Dict
```

### Media Messages (Video)

```python
# Upload video (typically .mp4 format)
video_key = bot.upload_file(file_path: str, file_type: str = "mp4") -> str

# Send to user
bot.send_media_to_user(user_open_id: str, file_key: str) -> Dict

# Send to chat
bot.send_media_to_chat(chat_id: str, file_key: str) -> Dict
```

### File Messages

```python
# Upload file
file_key = bot.upload_file(
    file_path: str,
    file_type: str = 'stream'  # 'stream', 'opus', 'mp4', 'pdf', 'doc', 'xls', 'ppt'
) -> str

# Send to user
bot.send_file_to_user(user_open_id: str, file_key: str) -> Dict

# Send to chat
bot.send_file_to_chat(chat_id: str, file_key: str) -> Dict

# Download file
bot.download_file(file_key: str, file_save_path: str) -> None
```

**Example**:

```python
# Upload PDF and send
pdf_key = bot.upload_file("/tmp/report.pdf", file_type="pdf")
bot.send_file_to_chat("oc_xxx", pdf_key)

# Download file
bot.download_file(pdf_key, "/save/path/report.pdf")
```

### Post Messages (Rich Text)

```python
# Send to user
bot.send_post_to_user(user_open_id: str, post_content: Dict) -> Dict

# Send to chat
bot.send_post_to_chat(chat_id: str, post_content: Dict) -> Dict
```

**Example** (see PostContent section for builder usage):

```python
from pywayne.lark_bot import PostContent

post = PostContent(title="Announcement")
post.add_markdown("**Important update**: System will be upgraded tonight")

bot.send_post_to_chat("oc_xxx", post.get_content())
```

### Interactive Card Messages

```python
# Send to user
bot.send_interactive_to_user(user_open_id: str, interactive: Dict) -> Dict

# Send to chat
bot.send_interactive_to_chat(chat_id: str, interactive: Dict) -> Dict
```

**Example with Raw Card JSON**:

```python
card = {
    "header": {
        "title": {"content": "Approval Request", "tag": "plain_text"},
        "template": "red"
    },
    "elements": [
        {"tag": "markdown", "content": "**Ticket #1234** needs approval"},
        {
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {"content": "Approve", "tag": "plain_text"},
                    "type": "primary",
                    "url": "https://example.com/approve/1234"
                }
            ]
        }
    ]
}

bot.send_interactive_to_chat("oc_xxx", card)
```

**Example with CardContentV2 Builder**:

```python
from pywayne.lark_bot import CardContentV2

card = CardContentV2(title="Status Update", template="green")
card.add_markdown("All systems operational ✅")
card.add_hr()
card.add_image("img_xxx", size="large")

bot.send_interactive_to_chat("oc_xxx", card.get_card())
```

### Share Messages

```python
# Share chat to user
bot.send_shared_chat_to_user(user_open_id: str, shared_chat_id: str) -> Dict

# Share chat to chat
bot.send_shared_chat_to_chat(chat_id: str, shared_chat_id: str) -> Dict

# Share user to user
bot.send_shared_user_to_user(user_open_id: str, shared_user_id: str) -> Dict

# Share user to chat
bot.send_shared_user_to_chat(chat_id: str, shared_user_id: str) -> Dict
```

### System Messages

```python
# Send system message to user (special divider-style message)
bot.send_system_msg_to_user(user_open_id: str, system_msg_text: str) -> Dict
```

## Message Lifecycle Management

### Reply to Message

Reply to an existing message with quote/reference.

```python
response = bot.reply_message(
    message_id: str,
    msg_type: str,                                    # "text", "image", "post", "interactive", etc.
    content: Union[str, Dict[str, Any], List[Any]],
    *,
    reply_in_thread: bool = False,                    # Reply in thread instead of main chat
    uuid: str = ""
) -> Dict
```

**Examples**:

```python
# Reply with text
bot.reply_message("om_xxx", "text", {"text": "Received your message"})

# Reply with card
from pywayne.lark_bot import CardContentV2

card = CardContentV2(title="Processing")
card.add_markdown("Your request is being processed...")

bot.reply_message("om_xxx", "interactive", card.get_card())

# Reply in thread
bot.reply_message(
    "om_xxx",
    "text",
    {"text": "Thread reply"},
    reply_in_thread=True
)
```

### Forward Message

Forward an existing message to another user or chat.

```python
response = bot.forward_message(
    message_id: str,
    receive_id: str,
    *,
    receive_id_type: str = "chat_id",  # "chat_id" or "open_id"
    uuid: str = ""
) -> Dict
```

**Example**:

```python
# Forward alert to on-call engineer
bot.forward_message(
    message_id="om_alert_xxx",
    receive_id="ou_engineer_xxx",
    receive_id_type="open_id"
)
```

### Recall Message

Recall/delete a message sent by the bot.

```python
response = bot.recall_message(message_id: str) -> Dict
```

**Example**:

```python
# Send temporary status message
msg = bot.send_text_to_chat("oc_xxx", "Processing...")

# Later recall it
bot.recall_message(msg["message_id"])
```

### Get Message

Retrieve details of a specific message.

```python
response = bot.get_message(
    message_id: str,
    *,
    user_id_type: str = "open_id"
) -> Dict
```

### Get Message List

Retrieve historical messages from a chat.

```python
response = bot.get_message_list(
    chat_id: str,
    start_time: str,           # Unix timestamp in milliseconds
    end_time: str,             # Unix timestamp in milliseconds
    *,
    sort_type: str = "",       # "ByCreateTimeAsc" or "ByCreateTimeDesc"
    page_size: int = 50,
    page_token: str = ""
) -> Dict
```

**Example**:

```python
# Get messages from last 24 hours
import time

end_time = str(int(time.time() * 1000))
start_time = str(int((time.time() - 86400) * 1000))

history = bot.get_message_list(
    chat_id="oc_xxx",
    start_time=start_time,
    end_time=end_time,
    sort_type="ByCreateTimeAsc"
)

for msg in history.get("items", []):
    print(msg["message_id"], msg["msg_type"])
```

### Update Message

Replace entire message content.

```python
response = bot.update_message(
    message_id: str,
    msg_type: str,
    content: Union[str, Dict[str, Any], List[Any]]
) -> Dict
```

### Patch Message

Partially update message content (commonly used for interactive cards).

```python
response = bot.patch_message(
    message_id: str,
    content: Union[str, Dict[str, Any], List[Any]]
) -> Dict
```

### Update Interactive Card

Convenience wrapper for updating interactive cards in place.

```python
response = bot.update_interactive_card(
    message_id: str,
    card: Dict[str, Any]
) -> Dict
```

**Example: Status Card Workflow**:

```python
from pywayne.lark_bot import CardContentV2

# Send initial "processing" card
card = CardContentV2(title="Task Status", template="blue")
card.add_markdown("⏳ Processing your request...")

msg = bot.send_interactive_to_chat("oc_xxx", card.get_card())

# ... perform task ...

# Update to "completed" card
completed_card = CardContentV2(title="Task Status", template="green")
completed_card.add_markdown("✅ Task completed successfully!")

bot.update_interactive_card(msg["message_id"], completed_card.get_card())
```

## Reactions, Pins, and Urgency

### Add Reaction

Add emoji reaction to a message.

```python
response = bot.add_reaction(
    message_id: str,
    emoji_type: str  # Feishu emoji code: "THUMBSUP", "OK", "HEART", "HAHA", etc.
) -> Dict
```

**Available emoji codes** (partial list):
- `THUMBSUP`, `THUMBSDOWN`
- `OK`, `HEART`, `HAHA`
- `WITTY`, `SURPRISED`, `FLUSHED`
- `SPEECHLESS`, `TEARING`, `ANGRY`

**Note**: Use Feishu's emoji codes, not Unicode characters. Full list: `PostContent.list_emoji_types()` opens documentation.

**Example**:

```python
# Add thumbs up
reaction = bot.add_reaction("om_xxx", "THUMBSUP")

# Store reaction_id for later removal
reaction_id = reaction["reaction_id"]
```

### Delete Reaction

Remove a previously added reaction.

```python
response = bot.delete_reaction(
    message_id: str,
    reaction_id: str
) -> Dict
```

### List Reactions

Get all reactions on a message.

```python
response = bot.list_reactions(
    message_id: str,
    *,
    reaction_type: str = "",       # Filter by emoji type
    user_id_type: str = "open_id",
    page_size: int = 50,
    page_token: str = ""
) -> Dict
```

### Pin Message

Pin a message in chat.

```python
response = bot.pin_message(message_id: str) -> Dict
```

### Unpin Message

Unpin a message in chat.

```python
response = bot.unpin_message(message_id: str) -> Dict
```

### List Pinned Messages

Get all pinned messages in a chat.

```python
response = bot.list_pinned_messages(
    chat_id: str,
    *,
    start_time: str = "",
    end_time: str = "",
    page_size: int = 50,
    page_token: str = ""
) -> Dict
```

**Example: Pin Important Reply**:

```python
# Reply to user question
reply = bot.reply_message("om_xxx", "text", {"text": "Official answer: ..."})

# Pin the reply for visibility
bot.pin_message(reply["message_id"])
```

### Get Message Read Users

Get list of users who read a message.

```python
response = bot.get_message_read_users(
    message_id: str,
    *,
    user_id_type: str = "open_id",
    page_size: int = 50,
    page_token: str = ""
) -> Dict
```

### Urgent Message

Send urgent notification for an existing message.

```python
response = bot.urgent_message(
    message_id: str,
    urgent_type: str,              # "app", "phone", or "sms"
    user_open_ids: List[str],
    *,
    user_id_type: str = "open_id"
) -> Dict
```

**Urgent Types**:
- `"app"`: In-app notification
- `"phone"`: Phone call
- `"sms"`: SMS text message

**Example: Alert On-Call Engineer**:

```python
# Send alert message
msg = bot.send_text_to_chat("oc_xxx", "🔴 Production database down!")

# Urgent notify on-call engineer
bot.urgent_message(
    msg["message_id"],
    urgent_type="phone",
    user_open_ids=["ou_oncall_xxx"]
)
```

## Read Receipt Events

```python
# Get read receipt info
receipts = bot.get_message_read_users(message_id="om_xxx")
for reader in receipts.get("items", []):
    print(f"{reader['user_id']} read at {reader['read_time']}")
```

## Chat Management

### Create Chat

Create a new group chat.

```python
response = bot.create_chat(
    name: str,
    user_open_ids: List[str],
    description: str = "",
    *,
    avatar: str = "",
    owner_open_id: str = "",
    bot_ids: Optional[List[str]] = None,
    set_bot_manager: bool = False,
    uuid: str = ""
) -> Dict
```

**Example**:

```python
# Create project chat
chat = bot.create_chat(
    name="Project Alpha",
    user_open_ids=["ou_a", "ou_b", "ou_c"],
    description="Alpha project collaboration",
    owner_open_id="ou_a"
)

chat_id = chat["chat_id"]
```

### Delete Chat

Delete a chat group.

```python
response = bot.delete_chat(chat_id: str) -> Dict
```

### Update Chat

Update chat information.

```python
response = bot.update_chat(
    chat_id: str,
    *,
    name: str = "",
    description: str = "",
    avatar: str = "",
    owner_open_id: str = ""
) -> Dict
```

**Example**:

```python
bot.update_chat(
    "oc_xxx",
    name="Project Alpha - Staging",
    description="Staging environment coordination"
)
```

### Add Members to Chat

Add users to a chat group.

```python
response = bot.add_members_to_chat(
    chat_id: str,
    user_open_ids: List[str],
    *,
    succeed_type: int = 0
) -> Dict
```

### Remove Members from Chat

Remove users from a chat group.

```python
response = bot.remove_members_from_chat(
    chat_id: str,
    user_open_ids: List[str]
) -> Dict
```

### Set Chat Admin

Add or remove chat administrators.

```python
response = bot.set_chat_admin(
    chat_id: str,
    user_open_ids: List[str],
    *,
    is_admin: bool = True  # True to add, False to remove
) -> Dict
```

**Example**:

```python
# Add admin
bot.set_chat_admin("oc_xxx", ["ou_leader"], is_admin=True)

# Remove admin
bot.set_chat_admin("oc_xxx", ["ou_leader"], is_admin=False)
```

### Transfer Chat Owner

Transfer chat ownership to another member.

```python
response = bot.transfer_chat_owner(
    chat_id: str,
    new_owner_open_id: str
) -> Dict
```

### Get Chat Announcement

Retrieve current chat announcement.

```python
response = bot.get_chat_announcement(chat_id: str) -> Dict
```

### Set Chat Announcement

Update chat announcement using Feishu's patch API.

```python
response = bot.set_chat_announcement(
    chat_id: str,
    *,
    requests: Union[str, List[str]],  # Patch operations
    revision: str = ""
) -> Dict
```

**Note**: This uses Feishu's patch operation format. See Feishu documentation for announcement patch operations.

## Message Resource Handling

### Download Message Resource

Download a specific resource (image, file, audio, video) from a message.

```python
success = bot.download_message_resource(
    message_id: str,
    resource_type: str,        # "image", "file", "audio", "video", "media"
    save_path: str,
    file_key: str = None       # Optional: specific resource key
) -> bool
```

**Example**:

```python
# Download image from message
bot.download_message_resource(
    message_id="om_xxx",
    resource_type="image",
    save_path="/tmp/message_image.png",
    file_key="img_xxx"
)
```

### Download All Message Resources

Download all resources embedded in a message.

```python
resources = bot.download_message_resources(
    message_id: str,
    message_content: str,  # JSON string from message content
    save_dir: str
) -> Dict[str, str]  # Returns {resource_type: save_path}
```

**Example**:

```python
# Get message first
msg = bot.get_message("om_xxx")

# Download all resources
resources = bot.download_message_resources(
    message_id="om_xxx",
    message_content=msg["body"]["content"],
    save_dir="/tmp/resources"
)

for resource_type, path in resources.items():
    print(f"Downloaded {resource_type}: {path}")
```

## User and Group Queries

### Get User Info

Query user information by email or mobile.

```python
users = bot.get_user_info(
    emails: List[str],
    mobiles: List[str]
) -> Optional[Dict]
```

**Example**:

```python
users = bot.get_user_info(
    emails=["alice@example.com"],
    mobiles=["13800138000"]
)

if users:
    for user in users:
        print(user["user_id"], user["name"])
```

### Get Group List

Get list of all groups the bot is in.

```python
groups = bot.get_group_list() -> List[Dict]
```

### Get Group Chat ID by Name

Find chat IDs matching a group name.

```python
chat_ids = bot.get_group_chat_id_by_name(group_name: str) -> List[str]
```

**Example**:

```python
# Find "Project Alpha" groups
chat_ids = bot.get_group_chat_id_by_name("Project Alpha")

if chat_ids:
    bot.send_text_to_chat(chat_ids[0], "Hello, team!")
```

### Get Members in Group

Get list of members in a chat group.

```python
members = bot.get_members_in_group_by_group_chat_id(
    group_chat_id: str
) -> List[Dict]
```

### Get Member Open ID by Name

Find member open IDs matching a name in a chat.

```python
open_ids = bot.get_member_open_id_by_name(
    group_chat_id: str,
    member_name: str
) -> List[str]
```

**Example**:

```python
# Find member in group
chat_ids = bot.get_group_chat_id_by_name("Project Alpha")
if chat_ids:
    member_ids = bot.get_member_open_id_by_name(chat_ids[0], "Alice")
    if member_ids:
        bot.send_text_to_user(member_ids[0], "Hi Alice!")
```

### Get Chat and User Name

Helper to get both chat name and user name in one call.

```python
chat_name, user_name = bot.get_chat_and_user_name(
    chat_id: str,
    user_id: str
) -> Tuple[str, str]
```

**Example**:

```python
chat_name, user_name = bot.get_chat_and_user_name("oc_xxx", "ou_xxx")
print(f"User {user_name} in chat {chat_name}")
```

## Batch Messaging

Send messages to multiple users or departments at once.

```python
response = bot.batch_send_message(
    msg_type: str,
    *,
    content: Optional[Union[str, Dict[str, Any], List[Any]]] = None,
    card: Optional[Dict[str, Any]] = None,
    user_open_ids: Optional[List[str]] = None,
    department_ids: Optional[List[str]] = None,
    user_ids: Optional[List[str]] = None,
    union_ids: Optional[List[str]] = None
) -> Dict
```

**Parameters**:
- `msg_type`: "text", "interactive", etc.
- `content`: Message content (for non-interactive types)
- `card`: Card content (for interactive type)
- Target lists (at least one required):
  - `user_open_ids`: List of user open IDs
  - `department_ids`: List of department IDs
  - `user_ids`: List of user IDs
  - `union_ids`: List of union IDs

**Important Notes**:
- Uses Feishu's `/message/v4/batch_send/` endpoint
- Batch messages cannot be replied to or updated like normal messages
- Only supports user/department targets, not chat groups

**Example: Send Notification to Multiple Users**:

```python
# Text to multiple users
bot.batch_send_message(
    "text",
    content="System maintenance tonight at 23:00",
    user_open_ids=["ou_a", "ou_b", "ou_c"]
)

# Card to department
from pywayne.lark_bot import CardContentV2

card = CardContentV2(title="Announcement", template="red")
card.add_markdown("**Important**: Please update your passwords")

bot.batch_send_message(
    "interactive",
    card=card.get_card(),
    department_ids=["od_engineering"]
)
```

## Complete Usage Examples

### Example 1: Comprehensive Release Workflow

```python
from pywayne.lark_bot import LarkBot, CardContentV2

bot = LarkBot(app_id="cli_xxx", app_secret="sec_xxx")

chat_id = "oc_xxx"

# Step 1: Send initial status card
card = CardContentV2(title="Deployment Status", template="blue")
card.add_markdown("⏳ Deployment started...")

msg = bot.send_interactive_to_chat(chat_id, card.get_card())
message_id = msg["message_id"]

# Step 2: Update progress
import time
time.sleep(5)

progress_card = CardContentV2(title="Deployment Status", template="blue")
progress_card.add_markdown("📦 Building Docker images... 50%")

bot.update_interactive_card(message_id, progress_card.get_card())

# Step 3: Update to completion
time.sleep(5)

done_card = CardContentV2(title="Deployment Status", template="green")
done_card.add_markdown("""
✅ Deployment completed successfully!

**Services Updated**:
- API: v1.2.3
- Frontend: v2.4.5
- Worker: v1.1.1

**Health Check**: All systems operational
""")

bot.update_interactive_card(message_id, done_card.get_card())

# Step 4: Pin the final status
bot.pin_message(message_id)
```

### Example 2: Interactive Support Ticket

```python
from pywayne.lark_bot import LarkBot, TextContent

bot = LarkBot(app_id="cli_xxx", app_secret="sec_xxx")

# User asks question in chat
# (Triggered by LarkBotListener - see lark-bot-listener skill)

# Reply with acknowledgment
reply_msg = bot.reply_message(
    "om_user_question",
    "text",
    {"text": "Processing your request..."}
)

# Add reaction to original question
bot.add_reaction("om_user_question", "THUMBSUP")

# Process request...
answer = "The solution is to restart the service"

# Update reply with answer
bot.update_message(
    reply_msg["message_id"],
    "text",
    {"text": f"✅ {answer}"}
)

# Pin the solution
bot.pin_message(reply_msg["message_id"])

# Remove processing reaction
# (reaction_id would be stored from add_reaction response)
```

### Example 3: Alert Forwarding with Urgency

```python
# Alert detected
alert_msg = bot.send_text_to_chat(
    "oc_alerts",
    "🔴 CRITICAL: Database connection timeout"
)

# Forward to on-call engineer
bot.forward_message(
    alert_msg["message_id"],
    "ou_oncall",
    receive_id_type="open_id"
)

# Send urgent notification
bot.urgent_message(
    alert_msg["message_id"],
    "app",
    ["ou_oncall"]
)
```

### Example 4: Dynamic Chat Creation and Management

```python
# Create incident response chat
incident_chat = bot.create_chat(
    name="Incident #1234 - DB Outage",
    user_open_ids=["ou_engineer_a", "ou_engineer_b", "ou_manager"],
    description="Emergency response for database outage",
    owner_open_id="ou_manager"
)

chat_id = incident_chat["chat_id"]

# Set admins
bot.set_chat_admin(chat_id, ["ou_engineer_a"], is_admin=True)

# Send initial briefing
from pywayne.lark_bot import CardContentV2

briefing = CardContentV2(title="Incident Briefing", template="red")
briefing.add_markdown("""
**Incident**: Database connection timeout
**Start Time**: 2026-03-12 14:35:00
**Impact**: Production API down
**Status**: Investigating

**Action Items**:
- Check database logs
- Review recent deployments
- Monitor connection pool
""")

bot.send_interactive_to_chat(chat_id, briefing.get_card())

# After incident resolved...
bot.update_chat(
    chat_id,
    name="[RESOLVED] Incident #1234 - DB Outage",
    description="Incident resolved - database connection restored"
)
```

### Example 5: Using send_markdown_to_chat with Tables

```python
from pywayne.lark_bot import LarkBot

bot = LarkBot(app_id="cli_xxx", app_secret="sec_xxx")

# Markdown report with table
report = """
# Weekly Test Report

## Summary
All critical tests passed this week.

## Results by Module

| Module      | Tests | Passed | Failed | Coverage |
| ----------- | ----- | ------ | ------ | -------- |
| Auth        | 145   | 145    | 0      | 95%      |
| Payment     | 89    | 87     | 2      | 87%      |
| API         | 234   | 230    | 4      | 92%      |
| Frontend    | 567   | 565    | 2      | 88%      |

## Next Steps
- Fix 8 failing tests
- Improve Payment module coverage
"""

# Send with post route and table fallback
bot.send_markdown_to_chat(
    "oc_xxx",
    md_text=report,
    title="Weekly Test Report",
    prefer="post",
    table_fallback="code_block"
)
```

## Common Patterns

### Pattern: Temporary Status Message

```python
# Send status
status_msg = bot.send_text_to_chat("oc_xxx", "⏳ Processing...")

# Do work...
import time
time.sleep(3)

# Recall temporary message
bot.recall_message(status_msg["message_id"])

# Send final result
bot.send_text_to_chat("oc_xxx", "✅ Processing complete")
```

### Pattern: Reaction-Based Workflow

```python
# Add "processing" reaction
reaction = bot.add_reaction("om_xxx", "WITTY")

try:
    # Process request
    result = process_request()
    
    # Reply with result
    bot.reply_message("om_xxx", "text", {"text": f"Result: {result}"})
finally:
    # Remove processing reaction
    bot.delete_reaction("om_xxx", reaction["reaction_id"])
```

### Pattern: Reply and Pin for Visibility

```python
# Reply with important information
reply = bot.reply_message(
    "om_question",
    "text",
    {"text": "Official policy: ..."}
)

# Pin for all members to see
bot.pin_message(reply["message_id"])
```

### Pattern: Message with Read Receipt Check

```python
# Send important message
msg = bot.send_text_to_chat("oc_xxx", "Please review the updated policy")

# Later check who read it
receipts = bot.get_message_read_users(msg["message_id"])
readers = [reader["user_id"] for reader in receipts.get("items", [])]

# Follow up with non-readers
all_members = bot.get_members_in_group_by_group_chat_id("oc_xxx")
non_readers = [m["member_id"] for m in all_members if m["member_id"] not in readers]

for user_id in non_readers:
    bot.send_text_to_user(user_id, "Reminder: please review the updated policy")
```

## Dependencies

```
lark-oapi>=1.2.0
pywayne>=0.1.0 (for tools integration)
```

## Important Notes

1. **Message Content Encoding**:
   - `reply_message`, `update_message`, `patch_message` automatically JSON-encode content
   - Text messages typically use `{"text": "message"}`
   - Interactive cards pass the card JSON directly

2. **Message IDs**:
   - Always store `message_id` from send responses for later operations
   - Message IDs are required for reply, forward, recall, update, reactions, pins

3. **Reaction Emoji Codes**:
   - Use Feishu's emoji type strings (e.g., `"THUMBSUP"`), not Unicode emojis
   - Get full list: `PostContent.list_emoji_types()` opens documentation

4. **Batch Send Limitations**:
   - Cannot reply to or update batch-sent messages
   - Only supports user/department targets
   - Different from normal group messages

5. **Chat Announcement**:
   - `set_chat_announcement` uses Feishu's patch API format
   - Requires understanding of Feishu announcement patch operations
   - Refer to Feishu OpenAPI documentation for patch request structure

6. **send_markdown_to_chat Advantages**:
   - Automatic byte-based chunking for large content
   - Table fallback for reliable rendering
   - Dual routing (card_v2/post) flexibility
   - **Recommended for all Markdown sending**

## Integration with LarkBotListener

For receiving and processing incoming messages, use `LarkBotListener` (separate skill):

```python
from pywayne.lark_bot_listener import LarkBotListener

listener = LarkBotListener(app_id="cli_xxx", app_secret="sec_xxx")

# Access bot instance
bot = listener.bot  # This is a LarkBot instance

@listener.text_handler()
async def handle_text(text: str, chat_id: str, message_id: str):
    # Reply using bot
    listener.bot.reply_message(message_id, "text", {"text": f"Echo: {text}"})

listener.run()
```

See `pywayne-lark-bot-listener` skill for complete listener documentation.
