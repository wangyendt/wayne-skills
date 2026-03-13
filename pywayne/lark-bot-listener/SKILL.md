---
name: pywayne-lark-bot-listener
description: Feishu/Lark message listener for real-time event processing via WebSocket. Use when users need to listen for incoming Feishu messages (text, image, file, audio, media, sticker, post, interactive) and events (recall, read, reaction, bot added/removed, member changes, chat updates) with automatic deduplication, async handling, resource auto-download, and convenient decorators. Provides high-level handlers (text_handler, image_handler, file_handler, audio_handler, media_handler, sticker_handler, mention_handler) with automatic download/cleanup and optional file回传, plus event handlers (recall_handler, message_read_handler, reaction_handler, bot_added/removed_handler, member_changed_handler, chat_updated/disbanded_handler), card action callback support, and listener-level streaming card helpers such as reply_streaming_card, update_streaming_card, recolor_streaming_card, stream_reply_card, and astream_reply_card.
---

# Pywayne Lark Bot Listener - Real-Time Event Processing

## Overview

`LarkBotListener` is a WebSocket-based event listener for Feishu (Lark) that enables **real-time message and event processing**. It provides decorator-based handlers for all message types and bot events, with automatic resource handling, message deduplication, and async/sync compatibility.

**Key Features**:
- **Message Handlers**: text, image, file, audio, media, sticker, post, interactive
- **Event Handlers**: recall, read, reaction, bot added/removed, member changes, chat updates
- **Auto Resource Handling**: Download images/files to temp dir, auto-cleanup after processing
- **Auto Upload/Send**: Return new file path from handler → automatically upload and send back
- **Flexible Parameters**: Handlers declare only parameters they need (text, chat_id, user_name, etc.)
- **Message Deduplication**: Per-handler deduplication with configurable expiry
- **Async/Sync Compatible**: Support both `async def` and `def` handler functions
- **Built-in LarkBot**: Access full `LarkBot` API via `listener.bot`
- **Streaming Reply Helpers**: Keep one card updated in place during long-running work
- **Card Action Callbacks**: HTTP handler for interactive card button clicks

**Companion**:
- Uses `LarkBot` internally for sending messages (see `pywayne-lark-bot` skill)

## Installation

```bash
pip install pywayne lark-oapi
```

## Quick Start

```python
from pywayne.lark_bot_listener import LarkBotListener

# Initialize listener
listener = LarkBotListener(
    app_id="cli_xxxxxxxxxxxx",
    app_secret="your_app_secret",
    message_expiry_time=60  # Deduplication expiry in seconds
)

# Handle text messages
@listener.text_handler()
async def on_text(text: str, chat_id: str):
    print(f"Received: {text}")
    listener.send_message(chat_id, f"Echo: {text}")

# Start listening
listener.run()
```

## LarkBotListener Class

### Constructor

```python
listener = LarkBotListener(
    app_id: str,
    app_secret: str,
    message_expiry_time: int = 60  # Deduplication cache expiry (seconds)
)
```

**Instance Attributes**:
- `bot`: Built-in `LarkBot` instance for sending messages and API calls
- `temp_dir`: Temporary directory for downloaded files (auto-created at system temp)

### Access Built-in Bot

```python
# Use bot for any LarkBot operations
listener.bot.send_text_to_chat("oc_xxx", "Message from listener")
listener.bot.reply_message("om_xxx", "text", {"text": "Reply"})
listener.bot.add_reaction("om_xxx", "THUMBSUP")
# ... any LarkBot method
```

## MessageContext

All low-level `@listen()` handlers receive a `MessageContext` object.

```python
from pywayne.lark_bot_listener import MessageContext

@listener.listen()
async def handle_any(ctx: MessageContext):
    print(ctx.chat_id)
    print(ctx.message_id)
    print(ctx.message_type)
```

**MessageContext Fields**:
- `chat_id`: Chat/conversation ID
- `user_id`: Sender's open ID
- `message_type`: Message type string ("text", "image", "file", etc.)
- `content`: Message content (text string or JSON string)
- `is_group`: Boolean indicating if message is from group chat
- `chat_type`: Feishu chat type ("group" or "p2p")
- `message_id`: Unique message ID
- `thread_id`: Thread ID if message is in a thread
- `root_id`: Root message ID for thread
- `parent_id`: Parent message ID for thread
- `mentions`: List of @mentions in message
- `raw_event`: Original Feishu SDK event object

## Core Message Handlers

### listen - Universal Message Entry Point

Generic message handler for any message type. Provides full `MessageContext`.

```python
@listener.listen(
    message_type: Optional[str] = None,  # Specific type or None for all
    group_only: bool = False,            # Only group messages
    user_only: bool = False              # Only private messages
)
async def handler(ctx: MessageContext):
    # Handler implementation
    pass
```

**Parameters**:
- `message_type`: Filter by type: `"text"`, `"image"`, `"file"`, `"audio"`, `"media"`, `"sticker"`, `"post"`, `"interactive"`, or `None` for all
- `group_only`: Only process group messages
- `user_only`: Only process private (p2p) messages

**Use Cases**:
- Need full message context
- Need `message_id` for replies, reactions, etc.
- Routing different message types from single handler
- Don't need automatic file download/upload

**Example: Universal Router**:

```python
@listener.listen()  # All message types
async def router(ctx: MessageContext):
    print(f"Message type: {ctx.message_type}")
    print(f"From {'group' if ctx.is_group else 'user'}: {ctx.chat_id}")
    print(f"Content: {ctx.content}")
    
    # Reply to any message
    listener.bot.reply_message(
        ctx.message_id,
        "text",
        {"text": f"Received {ctx.message_type} message"}
    )
```

**Example: Type-Specific Handling**:

```python
@listener.listen(message_type="post", group_only=True)
async def handle_group_posts(ctx: MessageContext):
    import json
    post_content = json.loads(ctx.content)
    print(f"Rich text post: {post_content}")
    
    # Add reaction
    listener.bot.add_reaction(ctx.message_id, "THUMBSUP")
```

### text_handler - Text Message Handler

Simplified handler for text messages with automatic parameter extraction.

```python
@listener.text_handler(
    group_only: bool = False,
    user_only: bool = False
)
async def handler(**kwargs):
    # Handler declares which parameters it needs
    pass
```

**Available Parameters** (declare any subset):
- `text` (str): Text message content
- `chat_id` (str): Chat ID
- `is_group` (bool): Whether from group
- `group_name` (str): Group name (empty for private chat)
- `user_name` (str): Sender's display name
- `message_id` (str): Message ID (for replies, requires manual declaration)

**Example: Simple Text Echo**:

```python
@listener.text_handler()
async def echo(text: str, chat_id: str):
    listener.send_message(chat_id, f"You said: {text}")
```

**Example: Group-Only Command Bot**:

```python
@listener.text_handler(group_only=True)
async def commands(text: str, chat_id: str, user_name: str):
    if text == "/status":
        listener.send_message(chat_id, f"{user_name}, system is healthy ✅")
    elif text == "/help":
        listener.send_message(chat_id, "Commands: /status, /help")
```

**Example: Context-Aware Response**:

```python
@listener.text_handler()
async def smart_reply(text: str, chat_id: str, is_group: bool, group_name: str, user_name: str):
    context = f"in {group_name}" if is_group else "in private"
    listener.send_message(
        chat_id,
        f"Hi {user_name}, I received your message {context}: {text}"
    )
```

### image_handler - Image Message Handler

Auto-downloads image to temp file, passes `Path` to handler. Optionally auto-uploads and sends returned image.

```python
@listener.image_handler(
    group_only: bool = False,
    user_only: bool = False
)
async def handler(**kwargs) -> Optional[Path]:
    # Handler returns new image path or None
    return processed_image_path  # Auto-uploads and sends
    # or
    return None  # No image sent back
```

**Available Parameters**:
- `image_path` (Path): Temporary image file path (required parameter)
- `chat_id` (str): Chat ID
- `is_group` (bool): Whether from group
- `group_name` (str): Group name
- `user_name` (str): Sender's display name
- `message_id` (str): Message ID

**Return Value**:
- `Path`: Automatically upload and send this image back to chat
- `None`: Don't send any image

**Auto-Cleanup**: Original downloaded image and returned image (if different) are automatically deleted after processing.

**Example: Simple Image Echo**:

```python
from pathlib import Path

@listener.image_handler()
async def echo_image(image_path: Path) -> Path:
    print(f"Received image: {image_path}")
    return image_path  # Send same image back
```

**Example: OpenCV Image Processing**:

```python
import cv2
import tempfile
from pathlib import Path

@listener.image_handler()
async def add_watermark(image_path: Path, user_name: str) -> Path:
    # Read image
    img = cv2.imread(str(image_path))
    
    # Add watermark
    cv2.putText(
        img,
        f"Processed by {user_name}",
        (30, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )
    
    # Save to new temp file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        result_path = Path(f.name)
    
    cv2.imwrite(str(result_path), img)
    
    return result_path  # Auto-upload and send
```

**Example: Conditional Processing**:

```python
@listener.image_handler(group_only=True)
async def process_group_images(image_path: Path, group_name: str) -> Optional[Path]:
    # Only process images from specific groups
    if group_name == "CV Project":
        # ... image processing ...
        return processed_path
    else:
        return None  # Don't send anything back
```

### file_handler - File Message Handler

Auto-downloads file to temp path. Optionally auto-uploads and sends returned file.

```python
@listener.file_handler(
    group_only: bool = False,
    user_only: bool = False
)
async def handler(**kwargs) -> Optional[Path]:
    # Handler returns new file path or None
    return processed_file_path  # Auto-uploads and sends
    # or
    return None  # No file sent back
```

**Available Parameters**:
- `file_path` (Path): Temporary file path
- `chat_id` (str): Chat ID
- `is_group` (bool): Whether from group
- `group_name` (str): Group name
- `user_name` (str): Sender's display name

**Return Value**: Same as `image_handler`

**Example: File Echo**:

```python
@listener.file_handler()
async def bounce_file(file_path: Path, user_name: str) -> Path:
    print(f"Received file from {user_name}: {file_path}")
    return file_path  # Send same file back
```

**Example: File Processing**:

```python
@listener.file_handler()
async def process_csv(file_path: Path, chat_id: str) -> Optional[Path]:
    # Check file extension
    if not str(file_path).endswith('.csv'):
        listener.send_message(chat_id, "Please send a CSV file")
        return None
    
    # Process CSV
    import pandas as pd
    df = pd.read_csv(file_path)
    
    # Create summary
    summary = df.describe()
    
    # Save summary to new file
    summary_path = file_path.with_suffix('.summary.csv')
    summary.to_csv(summary_path)
    
    return summary_path  # Send summary back
```

### audio_handler - Audio Message Handler

Auto-downloads audio file (typically `.opus` format).

```python
@listener.audio_handler(
    group_only: bool = False,
    user_only: bool = False
)
async def handler(**kwargs) -> Optional[Path]:
    # Return new audio path or None
    return processed_audio_path
```

**Available Parameters**:
- `audio_path` (Path): Temporary audio file path
- `chat_id` (str): Chat ID
- `is_group` (bool): Whether from group
- `group_name` (str): Group name
- `user_name` (str): Sender's display name
- `message_id` (str): Message ID
- `thread_id` (str): Thread ID

**Example: Audio Acknowledgment**:

```python
@listener.audio_handler()
async def on_audio(audio_path: Path, message_id: str):
    size = audio_path.stat().st_size
    listener.bot.reply_message(
        message_id,
        "text",
        {"text": f"Received audio: {size} bytes"}
    )
    # Return None - don't send audio back
    return None
```

### media_handler - Media/Video Message Handler

Auto-downloads media file (typically `.mp4` format).

```python
@listener.media_handler(
    group_only: bool = False,
    user_only: bool = False
)
async def handler(**kwargs) -> Optional[Path]:
    # Return new media path or None
    return processed_media_path
```

**Available Parameters**: Same as `audio_handler`, but parameter is `media_path`

**Example: Video Processing**:

```python
@listener.media_handler()
async def process_video(media_path: Path, chat_id: str) -> None:
    # Extract video metadata
    import cv2
    cap = cv2.VideoCapture(str(media_path))
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    
    cap.release()
    
    listener.send_message(
        chat_id,
        f"Video: {duration:.2f}s, {fps:.1f} FPS, {frame_count} frames"
    )
    
    return None  # Don't send video back
```

### sticker_handler - Sticker Message Handler

Handle Feishu sticker messages.

```python
@listener.sticker_handler(
    group_only: bool = False,
    user_only: bool = False
)
async def handler(**kwargs):
    pass
```

**Available Parameters**:
- `sticker_content` (dict or str): Parsed JSON content or raw string
- `raw_content` (str): Original raw content string
- `chat_id` (str): Chat ID
- `is_group` (bool): Whether from group
- `group_name` (str): Group name
- `user_name` (str): Sender's display name
- `message_id` (str): Message ID
- `thread_id` (str): Thread ID

**Example: Sticker Response**:

```python
@listener.sticker_handler()
async def on_sticker(sticker_content: dict, chat_id: str):
    sticker_key = sticker_content.get("file_key", "unknown")
    listener.send_message(chat_id, f"Nice sticker! ({sticker_key})")
```

### mention_handler - @Mention Handler

Only triggers when bot is @mentioned in messages.

```python
@listener.mention_handler(
    group_only: bool = False,
    user_only: bool = False
)
async def handler(**kwargs):
    pass
```

**Available Parameters**:
- `text` (str): Message text content
- `mentions` (list): List of @mention objects
- `chat_id` (str): Chat ID
- `is_group` (bool): Whether from group
- `group_name` (str): Group name
- `user_name` (str): Sender's display name
- `message_id` (str): Message ID
- `thread_id` (str): Thread ID
- `root_id` (str): Root message ID
- `parent_id` (str): Parent message ID
- `raw_event`: Original event object

**Example: Respond to @Mentions Only**:

```python
@listener.mention_handler(group_only=True)
async def when_mentioned(text: str, user_name: str, message_id: str):
    listener.bot.reply_message(
        message_id,
        "text",
        {"text": f"{user_name}, how can I help you?"}
    )
```

**Example: Command Parsing from @Mention**:

```python
@listener.mention_handler()
async def handle_commands(text: str, chat_id: str):
    # Remove @bot mention from text
    command = text.strip().lower()
    
    if "status" in command:
        listener.send_message(chat_id, "System status: ✅ Healthy")
    elif "help" in command:
        listener.send_message(chat_id, "Commands: status, help, ping")
    else:
        listener.send_message(chat_id, "Unknown command")
```

### Streaming Card Reply Helpers

These wrappers let a listener handler stream output back into one reply card without dropping down to raw `listener.bot` calls.

```python
reply = listener.reply_streaming_card(
    target: Union[str, MessageContext],
    *,
    title: str = "Streaming Reply",
    template: str = "blue",
    initial_md: str = "",
    reply_in_thread: bool = False,
    uuid: str = "",
    status_text: str = "Generating...",
    max_chunk_bytes: int = 18_000
) -> Dict

response = listener.update_streaming_card(
    card_message_id: str,
    md_text: str,
    *,
    title: str = "Streaming Reply",
    template: str = "blue",
    done: bool = False,
    status_text: str = "",
    max_chunk_bytes: int = 18_000
) -> Dict

response = listener.recolor_streaming_card(
    card_message_id: str,
    md_text: str,
    *,
    title: str = "Streaming Reply",
    template: str = "green",
    status_text: str = "Done",
    done: bool = True,
    max_chunk_bytes: int = 18_000
) -> Dict

result = listener.stream_reply_card(
    target: Union[str, MessageContext],
    text_stream: Iterable[Any],
    *,
    title: str = "Streaming Reply",
    template: str = "blue",
    initial_md: str = "",
    reply_in_thread: bool = False,
    uuid: str = "",
    update_interval: float = 0.25,
    status_text: str = "Generating...",
    final_status_text: str = "",
    final_template: Optional[str] = "green",
    max_chunk_bytes: int = 18_000
) -> Dict[str, Any]

result = await listener.astream_reply_card(
    target: Union[str, MessageContext],
    text_stream: AsyncIterable[Any],
    *,
    title: str = "Streaming Reply",
    template: str = "blue",
    initial_md: str = "",
    reply_in_thread: bool = False,
    uuid: str = "",
    update_interval: float = 0.25,
    status_text: str = "Generating...",
    final_status_text: str = "",
    final_template: Optional[str] = "green",
    max_chunk_bytes: int = 18_000
) -> Dict[str, Any]
```

**Key Rules**:
- `target` can be either a raw `message_id` or the whole `MessageContext`.
- `update_streaming_card()` updates the card message returned by `reply_streaming_card()`, not the original user message ID.
- Streaming updates expect the full accumulated Markdown, not the latest delta only.
- Use `final_template="green"` for success and `recolor_streaming_card(..., template="red")` for failure.
- If you need token-level refresh, decrease `update_interval`, but remember Feishu message updates are rate-limited.

**Example 1: Mention -> Async LLM Stream -> Auto Turn Green**:

```python
@listener.mention_handler(group_only=True)
async def answer_when_mentioned(text: str, user_name: str, message_id: str):
    async def fake_llm_stream():
        yield f"Hello {user_name}.\n\n"
        yield "## Draft answer\n"
        yield f"- You asked: `{text}`\n"
        yield "- Suggested next step: review the checklist.\n"

    await listener.astream_reply_card(
        message_id,
        fake_llm_stream(),
        title="Assistant Reply",
        template="blue",
        status_text="Thinking...",
        final_status_text="Answer complete",
        final_template="green",
        update_interval=0.4
    )
```

**Example 2: Universal Handler with Manual Progress Updates**:

```python
@listener.listen(message_type="text")
async def run_job(ctx: MessageContext):
    reply = listener.reply_streaming_card(
        ctx,
        title="Data Pipeline",
        template="wathet",
        initial_md="Queued job...",
        status_text="Starting"
    )

    card_message_id = reply["message_id"]
    current_text = "Queued job..."

    current_text += "\n- Loaded source files"
    listener.update_streaming_card(
        card_message_id,
        current_text,
        title="Data Pipeline",
        template="wathet",
        status_text="Transforming"
    )

    current_text += "\n- Applied transformations"
    listener.update_streaming_card(
        card_message_id,
        current_text,
        title="Data Pipeline",
        template="wathet",
        status_text="Uploading output"
    )

    listener.recolor_streaming_card(
        card_message_id,
        current_text + "\n- Upload completed",
        title="Data Pipeline",
        template="green",
        status_text="Finished"
    )
```

**Example 3: Add Reaction While Working, Remove It When Done**:

```python
@listener.listen(message_type="text")
async def process_with_progress(ctx: MessageContext):
    reaction = listener.bot.add_reaction(ctx.message_id, "OK")
    reaction_id = reaction.get("reaction_id", "")

    reply = listener.reply_streaming_card(
        ctx,
        title="Risk Review",
        template="blue",
        initial_md="Parsing request..."
    )
    card_message_id = reply["message_id"]
    current_text = "Parsing request..."

    try:
        for step in [
            "Loaded policy rules",
            "Matched request fields",
            "Generated recommendation",
        ]:
            current_text += f"\n- {step}"
            listener.update_streaming_card(
                card_message_id,
                current_text,
                title="Risk Review",
                template="blue",
                status_text="Running"
            )

        listener.recolor_streaming_card(
            card_message_id,
            current_text + "\n\n**Decision**: approved",
            title="Risk Review",
            template="green",
            status_text="Completed"
        )
    except Exception as exc:
        listener.recolor_streaming_card(
            card_message_id,
            current_text + f"\n\n**Error**: {exc}",
            title="Risk Review",
            template="red",
            status_text="Failed"
        )
        raise
    finally:
        if reaction_id:
            listener.bot.delete_reaction(ctx.message_id, reaction_id)
```

## Event Handlers

### recall_handler - Message Recall Event

Triggered when a message is recalled.

```python
@listener.recall_handler()
async def on_recall(**kwargs):
    pass
```

**Available Parameters**:
- `message_id` (str): ID of recalled message
- `chat_id` (str): Chat ID
- `recall_time` (str): Recall timestamp
- `recall_type` (str): Recall type
- `raw_event`: Original event object

**Example: Log Recalls**:

```python
@listener.recall_handler()
async def log_recalls(message_id: str, chat_id: str, recall_time: str):
    print(f"Message {message_id} recalled in {chat_id} at {recall_time}")
```

### message_read_handler - Message Read Event

Triggered when message(s) are marked as read.

```python
@listener.message_read_handler()
async def on_read(**kwargs):
    pass
```

**Available Parameters**:
- `reader`: Reader information object
- `message_id_list` (list): List of read message IDs
- `raw_event`: Original event object

**Example: Track Read Status**:

```python
@listener.message_read_handler()
async def track_reads(message_id_list: list, reader):
    for msg_id in message_id_list:
        print(f"Message {msg_id} read by {reader}")
```

### reaction_handler - Reaction Event

Triggered when reaction is added or removed.

```python
@listener.reaction_handler()
async def on_reaction(**kwargs):
    pass
```

**Available Parameters**:
- `action` (str): `"created"` or `"deleted"`
- `message_id` (str): Message ID
- `emoji_type` (str): Feishu emoji code (e.g., "THUMBSUP")
- `operator_type` (str): Operator type
- `user_id` (str): User who reacted
- `app_id` (str): App ID
- `action_time` (str): Timestamp
- `raw_event`: Original event object

**Example: Handle Reactions**:

```python
@listener.reaction_handler()
async def on_reaction(action: str, message_id: str, emoji_type: str, user_id: str):
    if action == "created":
        if emoji_type == "THUMBSUP":
            print(f"User {user_id} liked message {message_id}")
        elif emoji_type == "HEART":
            print(f"User {user_id} loved message {message_id}")
```

**Example: Reaction Event Triggers Batch Follow-Up**:

```python
@listener.reaction_handler()
async def escalate_on_reaction(action: str, emoji_type: str, user_id: str, message_id: str):
    if action != "created" or emoji_type != "OK":
        return

    listener.bot.batch_send_message(
        "text",
        content=f"Message {message_id} was acknowledged by {user_id}",
        user_open_ids=["ou_manager_a", "ou_manager_b"]
    )
```

### bot_added_handler - Bot Added to Group

Triggered when bot is added to a group chat.

```python
@listener.bot_added_handler()
async def on_added(**kwargs):
    pass
```

**Available Parameters**:
- `chat_id` (str): Chat ID
- `operator_id` (str): User who added the bot
- `external` (bool): Whether external group
- `operator_tenant_key` (str): Operator tenant key
- `name` (str): Group name
- `raw_event`: Original event object

**Example: Welcome Message**:

```python
@listener.bot_added_handler()
async def welcome(chat_id: str, name: str):
    listener.bot.send_markdown_to_chat(
        chat_id,
        md_text="""
# Bot Activated! 👋

Welcome to using our bot!

**Capabilities**:
- Auto-reply to messages
- Image processing
- File analysis
- @mention for help

Type `/help` to get started.
""",
        title="Welcome"
    )
```

### bot_removed_handler - Bot Removed from Group

Triggered when bot is removed from a group chat.

```python
@listener.bot_removed_handler()
async def on_removed(**kwargs):
    pass
```

**Available Parameters**: Same as `bot_added_handler`

**Example: Log Removal**:

```python
@listener.bot_removed_handler()
async def log_removal(chat_id: str, operator_id: str, name: str):
    print(f"Bot removed from {name} ({chat_id}) by {operator_id}")
```

### bot_p2p_chat_entered_handler - Bot Enters Private Chat

Triggered when bot enters a private chat with a user.

```python
@listener.bot_p2p_chat_entered_handler()
async def on_p2p_entered(**kwargs):
    pass
```

**Available Parameters**:
- `chat_id` (str): Chat ID
- `operator_id` (str): User's open ID
- `last_message_id` (str): Last message ID in chat
- `last_message_create_time` (str): Last message timestamp
- `raw_event`: Original event object

**Example: First-Time Welcome**:

```python
@listener.bot_p2p_chat_entered_handler()
async def first_contact(chat_id: str, operator_id: str):
    listener.bot.send_text_to_chat(
        chat_id,
        "Hello! I'm here to help. Ask me anything!"
    )
```

### member_changed_handler - Group Member Changes

Unified handler for member added/removed/withdrawn events.

```python
@listener.member_changed_handler()
async def on_member_change(**kwargs):
    pass
```

**Available Parameters**:
- `action` (str): `"added"`, `"deleted"`, or `"withdrawn"`
- `chat_id` (str): Chat ID
- `operator_id` (str): User who performed the action
- `users` (list): List of affected users
- `external` (bool): Whether external group
- `operator_tenant_key` (str): Operator tenant key
- `name` (str): Group name
- `raw_event`: Original event object

**Example: Member Change Notifications**:

```python
@listener.member_changed_handler()
async def notify_member_changes(action: str, chat_id: str, users: list, name: str):
    user_count = len(users)
    
    if action == "added":
        listener.bot.send_text_to_chat(
            chat_id,
            f"👋 Welcome {user_count} new member(s) to {name}!"
        )
    elif action == "deleted":
        listener.bot.send_text_to_chat(
            chat_id,
            f"{user_count} member(s) removed from {name}"
        )
    elif action == "withdrawn":
        listener.bot.send_text_to_chat(
            chat_id,
            f"{user_count} member(s) left {name}"
        )
```

### chat_updated_handler - Group Info Updated

Triggered when chat information changes (name, description, etc.).

```python
@listener.chat_updated_handler()
async def on_chat_updated(**kwargs):
    pass
```

**Available Parameters**:
- `chat_id` (str): Chat ID
- `operator_id` (str): User who made changes
- `external` (bool): Whether external group
- `operator_tenant_key` (str): Operator tenant key
- `before_change`: Info before change
- `after_change`: Info after change
- `moderator_list` (list): List of moderators
- `raw_event`: Original event object

**Example: Track Changes**:

```python
@listener.chat_updated_handler()
async def log_changes(chat_id: str, before_change, after_change):
    print(f"Chat {chat_id} updated:")
    print(f"  Before: {before_change}")
    print(f"  After: {after_change}")
```

### chat_disbanded_handler - Group Disbanded

Triggered when a group is disbanded/deleted.

```python
@listener.chat_disbanded_handler()
async def on_disbanded(**kwargs):
    pass
```

**Available Parameters**:
- `chat_id` (str): Chat ID
- `operator_id` (str): User who disbanded the group
- `external` (bool): Whether external group
- `operator_tenant_key` (str): Operator tenant key
- `name` (str): Group name
- `raw_event`: Original event object

**Example: Log Disbandment**:

```python
@listener.chat_disbanded_handler()
async def log_disbandment(chat_id: str, name: str, operator_id: str):
    print(f"Group '{name}' ({chat_id}) disbanded by {operator_id}")
```

## Interactive Card Callbacks

### card_action_handler - Card Button Click Handler

Register handler for interactive card action callbacks (button clicks, form submissions).

```python
@listener.card_action_handler(
    verification_token: str,
    encrypt_key: str = ""
)
def on_card_action(card_event):
    # Handle button click
    # Return response for toast/modal
    return {"toast": {"type": "success", "content": "Action completed"}}
```

**Returns**:
- Dict with toast/modal response
- Can update card content in place using `listener.bot.update_interactive_card()`

**Example: Approval Workflow**:

```python
@listener.card_action_handler(verification_token="your_token")
def handle_approval(card_event):
    action_value = card_event.action.value
    message_id = card_event.event.context.open_message_id
    
    if action_value == "approve":
        # Update card to show approved
        from pywayne.lark_bot import CardContentV2
        
        approved_card = CardContentV2(title="Approved", template="green")
        approved_card.add_markdown("✅ Request approved")
        
        listener.bot.update_interactive_card(message_id, approved_card.get_card())
        
        return {"toast": {"type": "success", "content": "Approved!"}}
    
    elif action_value == "reject":
        # Update card to show rejected
        from pywayne.lark_bot import CardContentV2
        
        rejected_card = CardContentV2(title="Rejected", template="red")
        rejected_card.add_markdown("❌ Request rejected")
        
        listener.bot.update_interactive_card(message_id, rejected_card.get_card())
        
        return {"toast": {"type": "warning", "content": "Rejected"}}
```

**Example: Button Click Recolors an Existing Streaming Card**:

```python
@listener.card_action_handler(verification_token="your_token")
def handle_review_action(card_event):
    message_id = card_event.event.context.open_message_id
    action = card_event.action.value.get("action")
    summary = card_event.action.value.get("summary", "No summary provided")

    if action == "approve":
        listener.bot.recolor_streaming_card(
            message_id,
            f"## Review Result\n\n{summary}",
            title="Manual Review",
            template="green",
            status_text="Approved"
        )
        return {"toast": {"type": "success", "content": "Approved"}}

    if action == "reject":
        listener.bot.recolor_streaming_card(
            message_id,
            f"## Review Result\n\n{summary}",
            title="Manual Review",
            template="red",
            status_text="Rejected"
        )
        return {"toast": {"type": "warning", "content": "Rejected"}}

    return {"toast": {"type": "info", "content": "No action taken"}}
```

### get_card_action_handler - Get HTTP Handler

Retrieve the HTTP handler for mounting in web frameworks.

```python
handler = listener.get_card_action_handler() -> CardActionHandler
```

**Usage with Flask**:

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/feishu/card', methods=['POST'])
def card_callback():
    handler = listener.get_card_action_handler()
    return handler(request)

app.run()
```

**Usage with FastAPI**:

```python
from fastapi import FastAPI, Request

app = FastAPI()

app.post("/feishu/card")(listener.get_card_action_handler())
```

## Utility Methods

### send_message - Quick Markdown Send

Lightweight method for sending Markdown-formatted messages.

```python
listener.send_message(chat_id: str, content: str) -> None
```

**Note**: Internally uses `PostContent` with Markdown. For more control, use `listener.bot.send_markdown_to_chat()`.

**Example**:

```python
listener.send_message(
    "oc_xxx",
    "**Bold** text and [link](https://example.com)"
)
```

### run - Start Listening

Start the WebSocket listener service.

```python
listener.run() -> None
```

**Important**: This is a blocking call. The listener will run until interrupted.

**Example**:

```python
# Register all handlers first
@listener.text_handler()
async def handle_text(text: str):
    print(text)

# Then start listening (blocking)
listener.run()
```

## Complete Usage Examples

### Example 1: AI Chat Bot

```python
from pywayne.lark_bot_listener import LarkBotListener
from pywayne.llm.chat_bot import ChatManager
import asyncio

listener = LarkBotListener(app_id="cli_xxx", app_secret="sec_xxx")

# Create AI chat manager
chat_manager = ChatManager(
    base_url="https://api.deepseek.com/v1",
    api_key="your_key"
)

@listener.text_handler()
async def ai_reply(text: str, chat_id: str, user_name: str):
    # Get or create chat instance for this conversation
    chat_bot = chat_manager.get_chat(chat_id)
    
    # Generate AI response (sync function, run in executor)
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: ''.join(chat_bot.chat(text, stream=True))
    )
    
    # Send response
    listener.send_message(chat_id, f"Hi {user_name}!\n\n{response}")

listener.run()
```

### Example 2: AprilTag Detection Bot

```python
from pywayne.lark_bot_listener import LarkBotListener
from pywayne.cv.apriltag_detector import ApriltagCornerDetector
from pathlib import Path
import cv2
import tempfile

listener = LarkBotListener(app_id="cli_xxx", app_secret="sec_xxx")
detector = ApriltagCornerDetector()

@listener.image_handler()
async def detect_apriltags(image_path: Path, user_name: str) -> Path:
    # Detect AprilTags in image
    detected_img = detector.detect_and_draw(str(image_path))
    
    # Save result to new temp file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        result_path = Path(f.name)
    
    cv2.imwrite(str(result_path), detected_img)
    
    # Return path - auto-uploads and sends
    return result_path

listener.run()
```

### Example 3: Multi-Handler Router

```python
from pywayne.lark_bot_listener import LarkBotListener, MessageContext

listener = LarkBotListener(app_id="cli_xxx", app_secret="sec_xxx")

# Handle text with command routing
@listener.text_handler(group_only=True)
async def commands(text: str, chat_id: str, user_name: str):
    if text.startswith("/"):
        command = text[1:].lower()
        
        if command == "status":
            listener.send_message(chat_id, "System: ✅ Healthy")
        elif command == "help":
            listener.send_message(chat_id, "Commands: /status, /help, /ping")
        elif command == "ping":
            listener.send_message(chat_id, f"Pong! Hi {user_name}")

# Handle images
@listener.image_handler()
async def process_image(image_path: Path) -> None:
    size = image_path.stat().st_size
    print(f"Received image: {size} bytes")
    return None  # Don't send back

# Handle @mentions specially
@listener.mention_handler()
async def when_mentioned(text: str, message_id: str):
    listener.bot.reply_message(
        message_id,
        "text",
        {"text": "You mentioned me! How can I help?"}
    )

# Handle reactions
@listener.reaction_handler()
async def on_reaction(action: str, emoji_type: str, message_id: str):
    if action == "created" and emoji_type == "THUMBSUP":
        print(f"Someone liked message {message_id}")

listener.run()
```

### Example 4: File Processing Pipeline

```python
from pywayne.lark_bot_listener import LarkBotListener
from pathlib import Path
import pandas as pd

listener = LarkBotListener(app_id="cli_xxx", app_secret="sec_xxx")

@listener.file_handler()
async def process_csv(file_path: Path, chat_id: str, user_name: str) -> Optional[Path]:
    # Check if CSV
    if not str(file_path).endswith('.csv'):
        listener.send_message(chat_id, f"{user_name}, please send a CSV file")
        return None
    
    try:
        # Load and process
        df = pd.read_csv(file_path)
        
        # Generate summary
        summary = df.describe()
        
        # Send text summary first
        summary_text = f"""
**CSV Analysis for {user_name}**

Rows: {len(df)}
Columns: {len(df.columns)}

Statistics:
{summary.to_markdown()}
"""
        listener.send_message(chat_id, summary_text)
        
        # Save detailed summary
        output_path = file_path.with_name(f"{file_path.stem}_summary.csv")
        summary.to_csv(output_path)
        
        # Return for auto-send
        return output_path
        
    except Exception as e:
        listener.send_message(chat_id, f"Error processing CSV: {e}")
        return None

listener.run()
```

### Example 5: Event-Driven Automation

```python
from pywayne.lark_bot_listener import LarkBotListener

listener = LarkBotListener(app_id="cli_xxx", app_secret="sec_xxx")

# Welcome new members
@listener.member_changed_handler()
async def welcome_members(action: str, chat_id: str, users: list):
    if action == "added":
        listener.bot.send_markdown_to_chat(
            chat_id,
            md_text=f"""
# 👋 Welcome!

Welcome to our group! We have {len(users)} new member(s).

**Getting Started**:
- Read pinned messages
- Check group description
- Introduce yourself

Type `/help` for bot commands.
""",
            title="Welcome"
        )

# Track reactions for analytics
@listener.reaction_handler()
async def track_reactions(action: str, emoji_type: str, message_id: str, user_id: str):
    if action == "created":
        # Log to analytics system
        print(f"Reaction: {user_id} added {emoji_type} to {message_id}")

# Bot added to new group
@listener.bot_added_handler()
async def on_added(chat_id: str, name: str):
    listener.bot.send_markdown_to_chat(
        chat_id,
        md_text=f"""
# 🤖 Bot Activated

Thanks for adding me to **{name}**!

**I can help with**:
- Auto-reply to messages
- Process images and files
- Answer questions
- Provide status updates

@mention me or type `/help` to get started.
""",
        title="Hello!"
    )

listener.run()
```

### Example 6: Advanced Reaction Workflow

```python
import asyncio

listener = LarkBotListener(app_id="cli_xxx", app_secret="sec_xxx")

@listener.listen(message_type="text")
async def process_with_reaction(ctx: MessageContext):
    # Add "processing" reaction
    reaction = listener.bot.add_reaction(ctx.message_id, "WITTY")
    reaction_id = reaction.get("reaction_id")
    
    try:
        # Simulate processing
        await asyncio.sleep(2)
        
        # Reply with result
        listener.bot.reply_message(
            ctx.message_id,
            "text",
            {"text": f"Processed: {ctx.content}"}
        )
    finally:
        # Remove processing reaction
        if reaction_id:
            listener.bot.delete_reaction(ctx.message_id, reaction_id)

listener.run()
```

### Example 7: Interactive Card with Callback

```python
from pywayne.lark_bot import CardContentV2

listener = LarkBotListener(app_id="cli_xxx", app_secret="sec_xxx")

# Send card when bot added to group
@listener.bot_added_handler()
async def send_welcome_card(chat_id: str):
    card = {
        "header": {
            "title": {"content": "Welcome Survey", "tag": "plain_text"},
            "template": "blue"
        },
        "elements": [
            {
                "tag": "markdown",
                "content": "Please complete our welcome survey"
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"content": "Start Survey", "tag": "plain_text"},
                        "type": "primary",
                        "value": "start_survey"
                    }
                ]
            }
        ]
    }
    
    listener.bot.send_interactive_to_chat(chat_id, card)

# Handle button click
@listener.card_action_handler(verification_token="your_token")
def on_button_click(card_event):
    action_value = card_event.action.value
    message_id = card_event.event.context.open_message_id
    
    if action_value == "start_survey":
        # Update card
        updated_card = CardContentV2(title="Thank You!", template="green")
        updated_card.add_markdown("✅ Survey link sent via private message")
        
        listener.bot.update_interactive_card(message_id, updated_card.get_card())
        
        return {"toast": {"type": "success", "content": "Survey started!"}}

listener.run()
```

## Best Practices

### 1. Handler Parameter Selection

Declare only parameters you need:

```python
# Good: Only declare needed parameters
@listener.text_handler()
async def simple(text: str):
    print(text)

# Good: Declare specific context
@listener.text_handler()
async def contextual(text: str, chat_id: str, user_name: str):
    print(f"{user_name} said {text} in {chat_id}")

# Avoid: Declaring unused parameters
@listener.text_handler()
async def wasteful(text: str, chat_id: str, is_group: bool, group_name: str, user_name: str):
    # Only using text
    print(text)
```

### 2. Resource Handling

Let handlers auto-cleanup:

```python
# Good: Return path for auto-upload
@listener.image_handler()
async def process(image_path: Path) -> Path:
    result = process_image(image_path)
    return result  # Auto-uploads and cleans up

# Good: Return None to skip sending
@listener.file_handler()
async def log_only(file_path: Path) -> None:
    log_file_info(file_path)
    return None  # No file sent back
```

### 3. Error Handling

Handlers have isolated exception handling:

```python
@listener.text_handler()
async def safe_handler(text: str, chat_id: str):
    try:
        # Your logic
        result = risky_operation(text)
        listener.send_message(chat_id, result)
    except Exception as e:
        # Error won't crash other handlers
        listener.send_message(chat_id, f"Error: {e}")
```

### 4. Async vs Sync

Both work, but async preferred:

```python
# Preferred: async
@listener.text_handler()
async def async_handler(text: str):
    await some_async_operation()

# Works: sync (auto-wrapped)
@listener.text_handler()
def sync_handler(text: str):
    some_sync_operation()
```

### 5. Use Built-in Bot for Advanced Features

```python
@listener.text_handler()
async def advanced(text: str, chat_id: str):
    # Use full LarkBot API
    msg = listener.bot.send_text_to_chat(chat_id, "Processing...")
    
    # Later update
    listener.bot.update_message(
        msg["message_id"],
        "text",
        {"text": "Done!"}
    )
    
    # Add reaction
    listener.bot.add_reaction(msg["message_id"], "THUMBSUP")
```

## Important Notes

1. **Message Deduplication**:
   - Each handler maintains its own deduplication cache
   - Same message can trigger multiple handlers
   - Default expiry: 60 seconds (configurable in constructor)
   - Prevents duplicate processing of the same message by same handler

2. **Temp File Management**:
   - Files downloaded to `{system_temp}/lark_bot_temp`
   - Auto-cleanup after handler completes
   - Returned files also cleaned up after upload

3. **Async Compatibility**:
   - All handlers support both `async def` and `def`
   - Internal async/sync detection and wrapping
   - Prefer `async def` for consistency

4. **Group/Private Filtering**:
   - `group_only=True`: Only process group messages
   - `user_only=True`: Only process private messages
   - Both False (default): Process all messages

5. **Parameter Flexibility**:
   - Handlers inspect function signature
   - Only declared parameters are passed
   - Allows concise handlers with minimal boilerplate

6. **Multiple Handler Registration**:
   - Can register multiple handlers for same message type
   - All matching handlers execute independently
   - Useful for different aspects (logging, processing, analytics)

7. **Card Callbacks**:
   - Require separate HTTP endpoint (Flask/FastAPI/etc.)
   - Use `get_card_action_handler()` to get handler
   - Mount handler at configured callback URL

## Dependencies

```
lark-oapi>=1.2.0
pywayne>=0.1.0 (for LarkBot)
cv2 (optional, for image processing)
```

## Integration with LarkBot

`LarkBotListener` uses `LarkBot` internally. Access it via `listener.bot`:

```python
listener = LarkBotListener(app_id="xxx", app_secret="xxx")

# Access full LarkBot API
listener.bot.send_text_to_chat("oc_xxx", "Message")
listener.bot.reply_message("om_xxx", "text", {"text": "Reply"})
listener.bot.add_reaction("om_xxx", "THUMBSUP")
listener.bot.create_chat("New Chat", ["ou_a", "ou_b"])
# ... all LarkBot methods available

# See pywayne-lark-bot skill for complete LarkBot documentation
```

## Complete Minimal Example

```python
from pywayne.lark_bot_listener import LarkBotListener

listener = LarkBotListener(
    app_id="cli_xxxxxxxxxxxx",
    app_secret="your_app_secret"
)

@listener.text_handler()
async def echo(text: str, chat_id: str):
    listener.send_message(chat_id, f"You said: {text}")

listener.run()  # Start listening (blocking)
```
