---
name: pywayne-lark-custom-bot
description: Feishu/Lark Custom Bot API wrapper for sending messages via webhook. Use when users need to send text messages, images, rich text posts, interactive cards, or share chat content to Feishu/Lark channels. Supports image upload from files or OpenCV/numpy images, signature verification for security, and @mention functionality. Ideal for one-way notifications, alerts, scheduled tasks, and simple push scenarios without message listening or two-way interaction requirements.
---

# Pywayne Lark Custom Bot - Webhook Message Sender

## Overview

`LarkCustomBot` is a webhook-based Feishu (Lark) bot wrapper designed for **one-way message pushing**. It's ideal for scenarios where you only need to send messages to Feishu groups without listening for incoming messages or managing complex interactions.

**Key Characteristics**:
- Lightweight, simple webhook-based architecture
- No event subscription or listening capabilities
- Perfect for alerts, notifications, scheduled tasks
- Supports signature verification for security

**When to Use LarkCustomBot**:
- Push-only scenarios (notifications, alerts, reports)
- Simple scheduled tasks sending updates
- Quick setup without event subscription configuration
- Don't need message replies, reactions, or chat management

**When to Use LarkBot Instead**:
- Need to listen and reply to messages
- Require message lifecycle management (recall, edit, reactions)
- Need chat management (members, admins, announcements)
- Interactive features like button callbacks

## Installation

```bash
pip install pywayne
```

## Quick Start

```python
from pywayne.lark_custom_bot import LarkCustomBot

# Initialize bot with webhook
bot = LarkCustomBot(
    webhook="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxx"
)

# Send simple text message
bot.send_text("Hello, Feishu!")

# Send text with @all mention
bot.send_text("Important announcement!", mention_all=True)
```

## LarkCustomBot Class

### Constructor

```python
bot = LarkCustomBot(
    webhook: str,              # Required: Webhook URL from Feishu group bot settings
    secret: str = '',          # Optional: Signing secret for request verification
    bot_app_id: str = '',      # Optional: App ID for image upload authentication
    bot_secret: str = ''       # Optional: App secret for image upload authentication
)
```

**Parameters**:
- `webhook`: Webhook URL obtained from Feishu group custom bot settings
- `secret`: Signing secret for signature verification (enhances security)
- `bot_app_id`: Required for `upload_image()` and `upload_image_from_cv2()`
- `bot_secret`: Required for `upload_image()` and `upload_image_from_cv2()`

**Note**: Image upload requires app credentials (`bot_app_id` and `bot_secret`) because it uses Feishu's OpenAPI authentication, not webhook.

## Core Methods

### send_text - Send Text Message

Send plain text message with optional @all mention.

```python
bot.send_text(text: str, mention_all: bool = False) -> None
```

**Parameters**:
- `text`: Message text content
- `mention_all`: Whether to @all users in the group (default `False`)

**Examples**:

```python
# Simple text
bot.send_text("Daily backup completed successfully")

# With @all mention
bot.send_text("System maintenance at 23:00 tonight", mention_all=True)

# Multi-line text
bot.send_text("""
Deployment completed:
- API: v1.2.3
- Frontend: v2.4.5
- Database migration: done
""")

# With HTML-like formatting (supported in text messages)
bot.send_text("<b>Bold text</b> and <i>italic text</i>")
```

### send_post - Send Rich Text Post

Send rich text message with structured content including text, links, @mentions, and images.

```python
bot.send_post(
    content: List[List[Dict]],      # 2D list of content elements
    title: Optional[str] = None     # Optional post title
) -> None
```

**Parameters**:
- `content`: 2D list structure where:
  - Outer list = multiple lines
  - Inner list = multiple elements in the same line
- `title`: Post title displayed at the top

**Content Structure**:

```python
content = [
    [element1, element2],  # Line 1 with 2 elements
    [element3],            # Line 2 with 1 element
    [element4, element5],  # Line 3 with 2 elements
]
```

**Basic Example**:

```python
from pywayne.lark_custom_bot import (
    LarkCustomBot,
    create_text_content,
    create_link_content,
    create_at_content,
    create_image_content
)

bot = LarkCustomBot(
    webhook="https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
    bot_app_id="cli_xxx",
    bot_secret="sec_xxx"
)

# Upload image first
image_key = bot.upload_image("/tmp/report.png")

# Construct post content
content = [
    # Line 1: Title text
    [create_text_content("Daily Report", unescape=False)],
    
    # Line 2: Link
    [create_link_content(href="https://dashboard.example.com", text="View Dashboard")],
    
    # Line 3: @mention
    [create_at_content(user_id="all", user_name="Everyone")],
    
    # Line 4: Image
    [create_image_content(image_key=image_key, width=400, height=300)],
    
    # Line 5: Multiple elements in one line
    [
        create_text_content("Status: "),
        create_text_content("✅ Completed", unescape=True)
    ]
]

bot.send_post(content, title="Daily Operations Report")
```

### send_image - Send Image Message

Send image message using image key.

```python
bot.send_image(image_key: str) -> None
```

**Note**: Must upload image first using `upload_image()` or `upload_image_from_cv2()`.

**Example**:

```python
# Upload and send local image
image_key = bot.upload_image("/path/to/chart.png")
bot.send_image(image_key)

# Upload from OpenCV image
import cv2
import numpy as np

img = cv2.imread("/path/to/image.jpg")
# Process image...
image_key = bot.upload_image_from_cv2(img)
bot.send_image(image_key)
```

### send_interactive - Send Interactive Card

Send interactive card message with buttons, forms, or other interactive elements.

```python
bot.send_interactive(card: Dict) -> None
```

**Parameters**:
- `card`: Interactive card JSON structure following Feishu card schema

**Example: Simple Notification Card**:

```python
card = {
    "config": {"wide_screen_mode": True},
    "header": {
        "title": {"tag": "plain_text", "content": "Approval Required"},
        "template": "red"
    },
    "elements": [
        {
            "tag": "markdown",
            "content": "**Ticket #1234** is waiting for approval"
        },
        {
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "View Details"},
                    "type": "primary",
                    "url": "https://example.com/ticket/1234"
                }
            ]
        }
    ]
}
bot.send_interactive(card)
```

**Example: Status Card with Multiple Elements**:

```python
card = {
    "header": {
        "title": {"tag": "plain_text", "content": "Build Status"},
        "template": "blue"
    },
    "elements": [
        {
            "tag": "div",
            "text": {"tag": "lark_md", "content": "**Build #456** completed"}
        },
        {
            "tag": "hr"
        },
        {
            "tag": "div",
            "fields": [
                {"is_short": True, "text": {"tag": "lark_md", "content": "**Duration**\n3m 42s"}},
                {"is_short": True, "text": {"tag": "lark_md", "content": "**Status**\n✅ Success"}}
            ]
        }
    ]
}
bot.send_interactive(card)
```

### send_share_chat - Share Chat

Share a chat group as a card.

```python
bot.send_share_chat(share_chat_id: str) -> None
```

**Example**:

```python
# Share a group chat
bot.send_share_chat("oc_a1b2c3d4e5f6g7h8")
```

## Image Upload Methods

### upload_image - Upload from File Path

Upload local image file to Feishu and get image key.

```python
image_key = bot.upload_image(file_path: str) -> str
```

**Parameters**:
- `file_path`: Local path to image file

**Returns**:
- `str`: Image key if successful, empty string if failed

**Example**:

```python
# Upload and send
image_key = bot.upload_image("/tmp/screenshot.png")
if image_key:
    bot.send_image(image_key)
else:
    print("Image upload failed")
```

**Requirements**:
- Must set `bot_app_id` and `bot_secret` in constructor
- File must exist and not be empty
- Supported formats: JPEG, PNG, GIF, etc.

### upload_image_from_cv2 - Upload from OpenCV Image

Upload image directly from OpenCV/numpy array.

```python
image_key = bot.upload_image_from_cv2(cv2_image: np.ndarray) -> str
```

**Parameters**:
- `cv2_image`: OpenCV image array (np.ndarray)

**Returns**:
- `str`: Image key if successful, empty string if failed

**Example: Generate and Send Visualization**:

```python
import cv2
import numpy as np

# Create visualization
img = np.zeros((400, 600, 3), dtype=np.uint8)
cv2.putText(img, "TEST PASSED", (80, 220), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 5)
cv2.rectangle(img, (50, 50), (550, 350), (0, 255, 0), 3)

# Upload and send directly
image_key = bot.upload_image_from_cv2(img)
bot.send_image(image_key)
```

**Example: Process and Send**:

```python
import cv2

# Read and process image
original = cv2.imread("/input/image.jpg")
gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, 50, 150)
edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

# Upload processed result
image_key = bot.upload_image_from_cv2(edges_colored)
bot.send_image(image_key)
```

**Use Cases**:
- Algorithm result visualization
- Real-time monitoring screenshots
- Computer vision processing results
- Generated charts and plots

## Content Builder Functions

These module-level functions help construct `send_post()` content elements.

### create_text_content

Create text content element.

```python
create_text_content(text: str, unescape: bool = False) -> Dict
```

**Parameters**:
- `text`: Text content
- `unescape`: Whether to unescape HTML entities (default `False`)

**Example**:

```python
text_elem = create_text_content("Normal text")
unescaped_elem = create_text_content("<b>Bold</b>", unescape=True)
```

### create_link_content

Create hyperlink content element.

```python
create_link_content(href: str, text: str) -> Dict
```

**Parameters**:
- `href`: URL link
- `text`: Display text for the link

**Example**:

```python
link_elem = create_link_content("https://www.feishu.cn", "Visit Feishu")
```

### create_at_content

Create @mention content element.

```python
create_at_content(user_id: str, user_name: str) -> Dict
```

**Parameters**:
- `user_id`: User ID or "all" for @everyone
- `user_name`: Display name for the mention

**Examples**:

```python
# @specific user
at_user = create_at_content("ou_xxxxxxxxxxxx", "John Doe")

# @everyone
at_all = create_at_content("all", "Everyone")
```

### create_image_content

Create image content element.

```python
create_image_content(
    image_key: str,
    width: Optional[int] = None,
    height: Optional[int] = None
) -> Dict
```

**Parameters**:
- `image_key`: Image key obtained from upload
- `width`: Optional image display width in pixels
- `height`: Optional image display height in pixels

**Example**:

```python
img_elem = create_image_content(
    image_key="img_v3_xxxxxxxxxxxx",
    width=500,
    height=300
)
```

## Common Usage Scenarios

### Scenario 1: Simple Scheduled Notification

```python
from pywayne.lark_custom_bot import LarkCustomBot

bot = LarkCustomBot(webhook="https://open.feishu.cn/open-apis/bot/v2/hook/xxx")

# Daily morning notification
bot.send_text("Good morning! Daily inspection started at 09:00")
```

### Scenario 2: Rich Announcement with Multiple Elements

```python
from pywayne.lark_custom_bot import (
    LarkCustomBot,
    create_text_content,
    create_link_content,
    create_at_content
)

bot = LarkCustomBot(webhook="https://open.feishu.cn/open-apis/bot/v2/hook/xxx")

content = [
    [create_text_content("Release v1.2.0 Completed", unescape=False)],
    [create_text_content("New Features:", unescape=False)],
    [create_text_content("  • API optimization")],
    [create_text_content("  • Bug fixes")],
    [create_link_content("https://example.com/release-notes", "View Release Notes")],
    [
        create_at_content("all", "Everyone"),
        create_text_content(" please review and confirm.")
    ]
]

bot.send_post(content, title="Release Announcement")
```

### Scenario 3: Upload and Send Local Image

```python
bot = LarkCustomBot(
    webhook="https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
    bot_app_id="cli_xxx",
    bot_secret="sec_xxx"
)

# Upload image file
image_key = bot.upload_image("/tmp/performance_chart.png")

if image_key:
    bot.send_image(image_key)
else:
    bot.send_text("Failed to upload image")
```

### Scenario 4: OpenCV Processing Pipeline

```python
import cv2
import numpy as np

bot = LarkCustomBot(
    webhook="https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
    bot_app_id="cli_xxx",
    bot_secret="sec_xxx"
)

# Generate test result visualization
img = np.zeros((400, 600, 3), dtype=np.uint8)

# Add test status
status = "PASS"
color = (0, 255, 0)  # Green
cv2.putText(img, status, (120, 220), cv2.FONT_HERSHEY_SIMPLEX, 3, color, 6)
cv2.rectangle(img, (30, 30), (570, 370), color, 3)

# Upload OpenCV image directly
image_key = bot.upload_image_from_cv2(img)
bot.send_image(image_key)
```

### Scenario 5: Combined Post with Text, Image, and Links

```python
from pywayne.lark_custom_bot import (
    LarkCustomBot,
    create_text_content,
    create_link_content,
    create_image_content
)

bot = LarkCustomBot(
    webhook="https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
    bot_app_id="cli_xxx",
    bot_secret="sec_xxx"
)

# Upload dashboard screenshot
image_key = bot.upload_image("/tmp/dashboard.png")

# Construct rich post
content = [
    [create_text_content("Monitoring Snapshot:")],
    [create_image_content(image_key, width=600, height=400)],
    [create_link_content("https://grafana.example.com", "Open Full Dashboard")],
    [create_text_content("Generated at: 2026-03-12 14:30:00")]
]

bot.send_post(content, title="Daily Monitoring Report")
```

### Scenario 6: Interactive Approval Card

```python
card = {
    "config": {"wide_screen_mode": True},
    "header": {
        "title": {"tag": "plain_text", "content": "Approval Request"},
        "template": "orange"
    },
    "elements": [
        {
            "tag": "markdown",
            "content": "**Deployment Request #5678**\n\nEnvironment: Production\nRequested by: John Doe"
        },
        {
            "tag": "hr"
        },
        {
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "Approve"},
                    "type": "primary",
                    "url": "https://example.com/approve/5678"
                },
                {
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "Reject"},
                    "type": "danger",
                    "url": "https://example.com/reject/5678"
                }
            ]
        }
    ]
}

bot.send_interactive(card)
```

### Scenario 7: Secure Sending with Signature Verification

```python
# Initialize with signature secret
bot = LarkCustomBot(
    webhook="https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
    secret="your_signing_secret"
)

# All messages will automatically include timestamp and signature
bot.send_text("This message is signed for security")
```

### Scenario 8: Multi-Step Operations Report

```python
from pywayne.lark_custom_bot import LarkCustomBot, create_text_content, create_link_content

bot = LarkCustomBot(
    webhook="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
)

# Step 1: Start notification
bot.send_text("🔄 Nightly inspection started...")

# Perform tasks...
# ... inspection logic ...

# Step 2: Send detailed report
content = [
    [create_text_content("✅ Nightly Inspection Completed", unescape=True)],
    [create_text_content("")],
    [create_text_content("Results:")],
    [create_text_content("  • Database backup: OK")],
    [create_text_content("  • Log cleanup: OK")],
    [create_text_content("  • Health check: OK")],
    [create_text_content("  • Disk usage: 42%")],
    [create_text_content("")],
    [create_link_content("https://monitoring.example.com", "View Detailed Report")]
]

bot.send_post(content, title="Inspection Report - 2026-03-12")
```

### Scenario 9: Share Group Chat Card

```python
# Share current group to another channel
bot.send_share_chat("oc_a1b2c3d4e5f6g7h8")
```

### Scenario 10: Monitoring Alert Pipeline

```python
import cv2
from pywayne.lark_custom_bot import LarkCustomBot, create_text_content, create_image_content

bot = LarkCustomBot(
    webhook="https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
    bot_app_id="cli_xxx",
    bot_secret="sec_xxx"
)

def send_alert(alert_type: str, message: str, screenshot_path: str):
    """Send alert with screenshot to Feishu group"""
    
    # Upload screenshot
    image_key = bot.upload_image(screenshot_path)
    
    # Choose emoji based on alert type
    emoji_map = {
        "critical": "🔴",
        "warning": "⚠️",
        "info": "ℹ️"
    }
    emoji = emoji_map.get(alert_type, "📢")
    
    # Construct alert message
    content = [
        [create_text_content(f"{emoji} Alert: {alert_type.upper()}", unescape=True)],
        [create_text_content("")],
        [create_text_content(message)],
        [create_image_content(image_key, width=500)]
    ]
    
    bot.send_post(content, title=f"{alert_type.title()} Alert")

# Usage
send_alert("warning", "CPU usage exceeded 80%", "/tmp/cpu_chart.png")
```

## Content Builder Functions Reference

All helper functions return `Dict` that can be used in `send_post()` content.

| Function | Purpose | Key Parameters |
|----------|---------|----------------|
| `create_text_content` | Plain or formatted text | `text`, `unescape` |
| `create_link_content` | Hyperlink | `href`, `text` |
| `create_at_content` | @mention user | `user_id`, `user_name` |
| `create_image_content` | Embed image | `image_key`, `width`, `height` |

## Error Handling

All methods include built-in logging and error handling:

```python
import logging

# The bot logs all operations
# Success: DEBUG level
# Errors: ERROR level with details

# Enable logging to see detailed output
logging.basicConfig(level=logging.DEBUG)

bot = LarkCustomBot(webhook="...")
bot.send_text("Test message")
# Logs: "Message sent successfully" or error details
```

**Common Errors**:

1. **Image upload fails**:
   - Missing `bot_app_id` or `bot_secret`
   - Empty image file
   - Invalid file format
   - Network issues

2. **Webhook request fails**:
   - Invalid webhook URL
   - Signature verification failed (check `secret`)
   - Rate limiting
   - Network timeout

## Security Features

### Signature Verification

When enabled, bot automatically signs all outgoing requests:

```python
bot = LarkCustomBot(
    webhook="https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
    secret="your_signing_secret"
)

# Automatic signature added to all requests
bot.send_text("Signed message")
```

**How it works**:
1. Generates HMAC-SHA256 signature using `timestamp + secret`
2. Includes `timestamp` and `sign` in request body
3. Feishu server verifies signature before processing

## Complete Example: Comprehensive Report

```python
from pywayne.lark_custom_bot import (
    LarkCustomBot,
    create_text_content,
    create_link_content,
    create_at_content,
    create_image_content
)
import cv2
import numpy as np

# Initialize bot with full credentials
bot = LarkCustomBot(
    webhook="https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
    secret="signing_secret",
    bot_app_id="cli_xxx",
    bot_secret="sec_xxx"
)

# Generate performance chart
chart = np.zeros((300, 500, 3), dtype=np.uint8)
cv2.putText(chart, "Performance: 95%", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

# Upload chart
chart_key = bot.upload_image_from_cv2(chart)

# Upload additional screenshot
screenshot_key = bot.upload_image("/tmp/dashboard.png")

# Construct comprehensive report
content = [
    [create_text_content("System Health Report", unescape=False)],
    [create_text_content("="*40)],
    [create_text_content("")],
    [create_text_content("📊 Performance Metrics:", unescape=True)],
    [create_image_content(chart_key, width=500, height=300)],
    [create_text_content("")],
    [create_text_content("🖥️ Dashboard Snapshot:", unescape=True)],
    [create_image_content(screenshot_key, width=600, height=400)],
    [create_text_content("")],
    [create_link_content("https://monitoring.example.com", "View Live Monitoring")],
    [create_text_content("")],
    [
        create_at_content("all", "All Members"),
        create_text_content(" - Please review the report.")
    ]
]

bot.send_post(content, title="Daily Health Report - 2026-03-12")

# Send completion notification
bot.send_text("✅ Daily report has been sent", mention_all=False)
```

## Comparison: LarkCustomBot vs LarkBot

| Feature | LarkCustomBot | LarkBot |
|---------|---------------|---------|
| **Setup** | Simple (webhook only) | Requires app configuration + event subscription |
| **Direction** | One-way (send only) | Two-way (send + receive) |
| **Use Case** | Notifications, alerts, reports | Interactive bots, auto-reply, chat management |
| **Message Types** | Text, post, image, card, share | All types + reply, forward, update, recall |
| **Image Upload** | ✅ Yes | ✅ Yes |
| **Listen Messages** | ❌ No | ✅ Yes (via LarkBotListener) |
| **Reply to Message** | ❌ No | ✅ Yes |
| **Reactions** | ❌ No | ✅ Yes |
| **Message Recall** | ❌ No | ✅ Yes |
| **Chat Management** | ❌ No | ✅ Yes |
| **Button Callbacks** | ❌ No | ✅ Yes |

**Decision Guide**:
- **Use LarkCustomBot** if: You only need to push messages, don't need responses
- **Use LarkBot** if: You need any form of two-way interaction or chat management

## Important Notes

1. **Image Upload Requirements**:
   - Must provide `bot_app_id` and `bot_secret` for image upload
   - Image upload uses Feishu OpenAPI authentication, not webhook
   - Empty files will be rejected with error log

2. **Content Structure**:
   - `send_post()` requires strict 2D list structure
   - Each inner list represents one line
   - Mix different content types in the same line

3. **Signature Security**:
   - Always use `secret` parameter in production for security
   - Signature is automatically generated and included in requests
   - Prevents unauthorized webhook access

4. **Interactive Cards**:
   - `send_interactive()` only sends cards, doesn't handle button clicks
   - Button callbacks require full app bot with event subscription
   - For interactive scenarios, migrate to `LarkBot` + `LarkBotListener`

5. **Rate Limiting**:
   - Feishu may rate-limit webhook requests
   - Consider adding retry logic for production use
   - Use `@retry` decorator from `pywayne.tools` for reliability

## Error Handling Best Practices

```python
from pywayne.tools import retry
from pywayne.lark_custom_bot import LarkCustomBot

bot = LarkCustomBot(webhook="https://open.feishu.cn/open-apis/bot/v2/hook/xxx")

# Add retry for reliability
@retry(max_tries=3, delay=1.0, backoff=2.0)
def send_with_retry(message: str):
    bot.send_text(message)

try:
    send_with_retry("Important notification")
except Exception as e:
    # Fallback notification method
    print(f"Failed to send after retries: {e}")
```

## Dependencies

```
requests>=2.25.0
requests-toolbelt>=0.9.0
numpy>=1.19.0 (optional, for upload_image_from_cv2)
opencv-python (optional, for upload_image_from_cv2)
```
