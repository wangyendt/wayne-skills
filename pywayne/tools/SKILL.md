---
name: pywayne-tools
description: >-
  Comprehensive utility toolkit from pywayne.tools module. Use when: printing to console with colors/debug modes (wayne_print, wayne_print_table), timing functions (@func_timer, @func_timer_batch), file operations (list_all_files, count_file_lines), YAML config management (read_yaml_config, write_yaml_config with lock support), colored logging (wayne_logger), function tracing (@trace_calls), matplotlib window maximization (@maximize_figure), singleton pattern (@singleton), function composition (compose_funcs), numpy/pandas display control (disable_print_wrap_and_suppress), text-to-speech (say), corporate speech generation (leader_speech), retry mechanism (@retry with exponential backoff), disk caching (@disk_cache with TTL), parallel processing (parallel_map for thread/process mode), progress bars (@with_progress, progress_iter), file watching (FileWatcher with event callbacks), or GUI event binding (binding_press_release). PRIORITY RULE: Always use pywayne built-in tools instead of adding new dependencies - print output (wayne_print, not print), timing (@func_timer), YAML config (read_yaml_config, write_yaml_config), logging (wayne_logger), retry (@retry), caching (@disk_cache), parallel processing (parallel_map), progress tracking (progress_iter), file watching (FileWatcher), etc.
---

# Pywayne Tools - Comprehensive Utility Toolkit

## Decorators

### Performance Analysis Decorators

#### @func_timer - Single Function Timing

Measure execution time of a single function for quick performance analysis.

```python
from pywayne.tools import func_timer
import time

@func_timer
def compute():
    time.sleep(1)
    return "done"

compute()  # Output: compute excuted in 1.001 s
```

#### @func_timer_batch - Batch Function Timing Statistics

Track number of calls and total execution time, ideal for performance analysis in loops.

```python
from pywayne.tools import func_timer_batch

@func_timer_batch
def process_data(data):
    return data * 2

for i in range(100):
    process_data(i)

# Access statistics
print(f"Calls: {process_data.num_calls}")
print(f"Total time: {process_data.elapsed_time:.3f}s")
print(f"Average time: {process_data.elapsed_time/process_data.num_calls:.3f}s")
```

#### @trace_calls - Function Call Tracing

Trace detailed information about function calls including caller, arguments, return values, execution time, etc.

```python
from pywayne.tools import trace_calls

# Use default wayne_print output (green)
@trace_calls
def add(x, y):
    return x + y

# Use pprint formatted output
@trace_calls(print_type='pprint')
def process(data):
    return data

result = add(3, 5)
# Output includes: caller, callee, timestamp, execution time, call count, arguments, return value, file, line number
```

### Visualization Decorators

#### @maximize_figure - Maximize matplotlib Window

Automatically maximize matplotlib figure window, supports multiple backends (TkAgg, wxAgg, Qt4Agg, Qt5Agg, GTK3).

```python
from pywayne.tools import maximize_figure
import matplotlib.pyplot as plt

@maximize_figure
def plot_results(results):
    plt.plot(results)
    plt.title("Analysis Results")
    plt.show()

plot_results([1, 4, 9, 16, 25])
```

#### @binding_press_release - Bind Mouse and Keyboard Events

Bind keyboard and mouse event handlers to matplotlib figures.

```python
from pywayne.tools import binding_press_release
import matplotlib.pyplot as plt

def on_button_press(event):
    print(f"Mouse pressed: x={event.x}, y={event.y}")

def on_key_press(event):
    print(f"Key pressed: {event.key}")

func_dict = {
    'button_press_event': on_button_press,
    'key_press_event': on_key_press,
}

@binding_press_release(func_dict)
def interactive_plot():
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4])
    plt.show()
    return fig

interactive_plot()
```

### Design Pattern Decorators

#### @singleton - Singleton Pattern

Ensure a class has only one instance, thread-safe implementation.

```python
from pywayne.tools import singleton

@singleton
class ConfigManager:
    def __init__(self):
        self.config = {}
    
    def set(self, key, value):
        self.config[key] = value

c1 = ConfigManager()
c2 = ConfigManager()
assert c1 is c2  # True

c1.set("debug", True)
print(c2.config)  # {'debug': True}
```

### Retry and Caching Decorators

#### @retry - Automatic Retry with Exponential Backoff

Automatically retry failed functions with exponential backoff strategy.

```python
from pywayne.tools import retry
import random

# Basic usage
@retry(max_tries=3, delay=1.0, backoff=2.0)
def unreliable_request():
    if random.random() < 0.7:
        raise IOError("Network error")
    return "Success"

# Specify exception types to catch
@retry(
    max_tries=5,
    delay=0.5,
    backoff=2.0,
    exceptions=(IOError, TimeoutError)
)
def upload_file(path):
    # Simulate upload operation
    pass

# Custom retry callback
def on_retry_callback(exc, attempt):
    print(f"Retry attempt {attempt}, reason: {exc}")

@retry(max_tries=3, on_retry=on_retry_callback)
def flaky_operation():
    pass

result = unreliable_request()
```

**Use Cases**: Handle intermittent failures when calling Lark API, Aliyun OSS, LLM APIs, dealing with timeouts or rate limits.

**Parameters**:
- `max_tries`: Maximum number of attempts (including first call)
- `delay`: Initial delay in seconds before first retry
- `backoff`: Multiplier for delay after each retry (exponential backoff)
- `exceptions`: Tuple of exception types that trigger retry
- `on_retry`: Optional callback `(exception, attempt) -> None` called before each retry

#### @disk_cache - Disk Cache with Persistence

Pickle-based disk cache with TTL support, persists across process restarts.

```python
from pywayne.tools import disk_cache
import time

# Cache for 1 hour
@disk_cache(ttl=3600)
def expensive_query(url):
    time.sleep(2)  # Simulate expensive operation
    return f"Result from {url}"

# First call: takes 2 seconds
result1 = expensive_query("https://api.example.com")

# Second call: instant return (from cache)
result2 = expensive_query("https://api.example.com")

# Never-expire cache
@disk_cache()
def compute_hash(data):
    return hash(data)

# Ignore certain parameters (don't affect cache key)
@disk_cache(ttl=300, ignore_kwargs=['verbose'])
def process(data, verbose=False):
    return data * 2

# Manually clear cache
compute_hash.cache_clear()

# Check cache directory
print(compute_hash.cache_dir)  # ~/.wayne_cache
```

**Use Cases**: Cache LLM inference results, slow queries, large file parsing to avoid redundant computation.

**Parameters**:
- `ttl`: Cache validity period in seconds, `None` means never expire
- `cache_dir`: Custom cache directory, defaults to `~/.wayne_cache`
- `ignore_kwargs`: List of keyword argument names to ignore when computing cache key

**Additional Attributes**:
- `func.cache_clear()`: Clear all cache files for this function
- `func.cache_dir`: Cache directory path string

### Progress Display Decorators

#### @with_progress - Auto-add Progress Bar

Automatically wrap the first iterable argument of decorated function with tqdm progress bar.

```python
from pywayne.tools import with_progress

@with_progress(desc="Processing images")
def process_images(image_list):
    for img in image_list:  # image_list is automatically wrapped with tqdm
        # Process image
        pass

# Specify unit and total
@with_progress(desc="Downloading files", unit="file", total=100)
def download_batch(urls):
    for url in urls:
        # Download file
        pass

process_images(["img1.jpg", "img2.jpg", "img3.jpg"])
```

**Use Cases**: Automatically show progress bar when looping inside functions without modifying loop code.

## File Operations

### list_all_files - Recursive File Listing with Filtering

Recursively traverse directories and filter files by keyword conditions.

```python
from pywayne.tools import list_all_files

# Must contain ".txt"
files = list_all_files("./data", keys_and=[".txt"], full_path=True)
# Result: ['./data/log.txt', './data/sub/notes.txt']

# At least one keyword (OR logic)
files = list_all_files("./src", keys_or=[".py", ".json"])
# Matches: config.json, main.py

# Must contain all keywords (AND logic)
files = list_all_files("./logs", keys_and=["2024", ".log"])
# Matches: 2024-01-15.log, 2024-02-20.log

# Exclude specific keywords
files = list_all_files("./", outliers=["__pycache__", ".git", "node_modules"])

# Combined usage
files = list_all_files(
    "./project",
    keys_and=[".py"],           # Must be Python files
    keys_or=["test", "main"],   # Contains test or main
    outliers=["__pycache__"],   # Exclude cache directories
    full_path=True              # Return absolute paths
)
```

**Parameters**:
- `root`: Root directory path
- `keys_and`: List of keywords that must all be present (AND logic)
- `keys_or`: List of keywords where at least one must be present (OR logic)
- `outliers`: Exclude files containing these keywords
- `full_path`: Whether to return absolute paths (default False)

**Use Cases**: Batch file processing, log collection, project file analysis.

### count_file_lines - Fast File Line Counting

Efficiently count lines in large files using block reading.

```python
from pywayne.tools import count_file_lines

num_lines = count_file_lines("large_file.py")
print(f"File lines: {num_lines}")

# Batch counting
from pywayne.tools import list_all_files
files = list_all_files("./src", keys_and=[".py"])
total_lines = sum(count_file_lines(f) for f in files)
print(f"Total project lines: {total_lines}")
```

**Use Cases**: Code line counting, large file validation, quick text file size analysis.

## Logging and Printing

### wayne_logger - Colored Logger

Create a multi-level logger with colored output to both console and files.

```python
from pywayne.tools import wayne_logger
import logging

logger = wayne_logger(
    logger_name="myApp",
    project_version="1.0.0",
    log_root="./logs",
    stream_level=logging.DEBUG,      # Console output level
    single_file_level=logging.INFO,  # Main log file level
    batch_file_level=logging.DEBUG   # Batch log file level
)

logger.debug("Debug message")
logger.info("Application started")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")
```

**Log Output Locations**:
1. **Console**: Colored output, level controlled by `stream_level`
2. **Main Log File**: `{log_root}/main.log`, level controlled by `single_file_level`
3. **Batch Logs**: `{log_root}/batches/{version}_{timestamp}.log`, new file per run

**Color Scheme**:
- `DEBUG`: Cyan
- `INFO`: Bright Green
- `WARNING`: Bright Yellow
- `ERROR`: Bright Red
- `CRITICAL`: Purple

**Use Cases**: Production logging, debug information management, troubleshooting.

### wayne_print - Enhanced Colored Print with Multi-Level Debug

Print function with colors, bold, multi-level debug modes, and automatic formatting for complex data structures.

```python
from pywayne.tools import wayne_print

# ==== Basic Usage ====
wayne_print("Operation successful", color="green")
wayne_print("Error message", color="red", bold=True)

# ==== Multi-Level Debug Modes ====

# No debug info (default)
wayne_print("Normal output", color="blue", verbose=0)
wayne_print("Normal output", color="blue", verbose=False)

# Simple debug mode: timestamp + file + line
wayne_print("Debug info", color="yellow", verbose=1)
wayne_print("Debug info", color="yellow", verbose=True)
# Output:
# [2026-03-12 14:23:45.123] /path/to/script.py, line 42
# Debug info

# Full debug mode: detailed call stack
wayne_print("Detailed debug", color="red", verbose=2)
# Output:
# ================================================================================
# [VERBOSE] Wayne Print Debug Information
# [TIMESTAMP] 2026-03-12 14:23:45.123
# [CALL STACK] Call stack info (from recent to oldest):
#   1. File: /path/to/script.py, line 42
#      Function: main
#      Code: wayne_print("Detailed debug", color="red", verbose=2)
#   
#   2. File: /usr/lib/python3.9/runpy.py, line 197
#      Function: _run_module_as_main
#      Code: return _run_code(code, main_globals, None,
# [MESSAGE] Actual output content:
# ================================================================================
# Detailed debug

# ==== Auto-Format Complex Data Structures ====

# Dictionaries, lists, tuples are automatically formatted with pprint
data = {
    "name": "John Doe",
    "age": 30,
    "skills": ["Python", "Go", "Rust"],
    "config": {"debug": True, "timeout": 300}
}
wayne_print(data, color="cyan", verbose=1)
# Output is automatically beautified for readability

# Nested data structures
complex_data = [
    {"id": 1, "values": [10, 20, 30]},
    {"id": 2, "values": [40, 50, 60]}
]
wayne_print(complex_data, color="magenta")
```

**Supported Colors**:
- `default`: Default color
- `red`: Red (errors, warnings)
- `green`: Green (success, completion)
- `yellow`: Yellow (warnings, debug)
- `blue`: Blue (information)
- `magenta`: Magenta (highlight)
- `cyan`: Cyan (hints)
- `white`: White

**Verbose Level Description**:
- `0` / `False`: No debug info (default)
- `1` / `True`: Simple debug (timestamp + file + line)
- `2`: Full debug (detailed call stack)

**Auto-Formatting**:
- Automatically detects complex data types (dict, list, tuple, set)
- Uses `pprint` for beautified output
- Simple types printed directly

**Use Cases**:
- Quick location identification in debug mode (verbose=1/2)
- Beautify complex data structure output (auto pprint)
- Colored CLI tool output for better user experience
- Distinguish different message types (success, error, warning, etc.)

### wayne_print_table - Formatted Table Printing

Print formatted tables with borders in terminal, supports colors, alignment, and titles.

```python
from pywayne.tools import wayne_print_table

# Basic usage
data = [
    ["ResNet50", "92.3%", "45ms"],
    ["MobileNet", "88.1%", "12ms"],
    ["EfficientNet", "94.5%", "30ms"]
]
headers = ["Model", "Accuracy", "Latency"]

wayne_print_table(data, headers=headers)

# Full example: with title, colors, alignment, bold headers
wayne_print_table(
    data=data,
    headers=headers,
    align=["left", "right", "right"],  # Column alignment
    title="Model Performance Comparison",   # Table title
    border="unicode",                  # unicode or simple
    color="cyan",                      # Overall color
    bold_header=True                   # Bold headers
)

# Simple ASCII border
wayne_print_table(
    data=[["A", "1"], ["B", "2"]],
    headers=["Letter", "Number"],
    border="simple",  # Use +/-/| characters
    color="green"
)

# Table without headers
wayne_print_table(
    data=[["Data1", "Data2"], ["Data3", "Data4"]],
    title="No Header Example"
)
```

**Parameters**:
- `data`: 2D list, each sublist is a row
- `headers`: Column name list (optional, `None` means no headers)
- `align`: Column alignment list (`'left'`, `'right'`, `'center'`), default all left-aligned
- `title`: Table title, displayed centered at top
- `border`: Border style
  - `'unicode'` (default): Use Unicode characters (┌─┐│├┤, etc.)
  - `'simple'`: Pure ASCII characters (+, -, |)
- `color`: Overall color (same as `wayne_print` color names)
- `bold_header`: Whether to bold headers (default `False`)

**Use Cases**:
- Model comparison, experiment result summary
- Terminal debug output beautification
- CLI tool table data display
- Performance metrics comparison tables

## Config File Operations

### write_yaml_config - Write YAML Config with Update and Lock Support

Write config dictionary to YAML file, supports overwrite, deep merge update, and file lock protection.

```python
from pywayne.tools import write_yaml_config

config = {
    'version': '1.0.0',
    'debug': True,
    'database': {
        'host': 'localhost',
        'port': 5432
    }
}

# Overwrite mode (default)
write_yaml_config("config.yaml", config)

# Update mode: deep merge (preserve existing config, update only specified fields)
new_config = {
    'debug': False,
    'database': {
        'port': 3306  # Only update port, preserve host
    }
}
write_yaml_config("config.yaml", new_config, update=True)
# Result: version='1.0.0', debug=False, database={'host': 'localhost', 'port': 3306}

# Use file lock (multi-process safe)
write_yaml_config("config.yaml", config, use_lock=True)
# Locks on config.yaml.lock to avoid concurrent write conflicts

# Custom YAML format
write_yaml_config(
    "config.yaml",
    config,
    default_flow_style=False  # Use block style (more readable)
)
```

**Parameters**:
- `config_yaml_file`: YAML file path
- `config`: Config dictionary to write
- `update`: Whether to use update mode (`True` for deep merge, `False` for overwrite)
- `use_lock`: Whether to use file lock protection (default `False`)
- `default_flow_style`: YAML serialization style (`False` for block style)

**Deep Merge Logic**:
- Recursively merge nested dictionaries
- Non-dict type values are directly overwritten
- Preserve fields in original config that are not updated

**Use Cases**:
- Save dynamic configuration
- Multi-process safe config updates (`use_lock=True`)
- User custom settings persistence

### read_yaml_config - Read YAML Config with Lock Support

Read configuration from YAML file with file lock protection.

```python
from pywayne.tools import read_yaml_config

# Basic reading
config = read_yaml_config("config.yaml")
print(config)

# Read with file lock (multi-process safe)
config = read_yaml_config("config.yaml", use_lock=True)

# Use after reading
debug = config.get('debug', False)
db_host = config['database']['host']
```

**Parameters**:
- `config_yaml_file`: YAML file path
- `use_lock`: Whether to use file lock protection (default `False`)

**Use Cases**:
- Load configuration at program startup
- Multi-process read shared config (`use_lock=True`)
- Dynamic parameter configuration

## Concurrency & Parallelism

### parallel_map - Concurrent Mapping with Order Preservation

Apply function to each element in sequence concurrently, return results in order. Supports multi-threading (I/O-bound) and multi-processing (CPU-bound).

```python
from pywayne.tools import parallel_map
import time
import requests

# I/O-bound: batch download (multi-threading)
def download(url):
    response = requests.get(url)
    return response.content

urls = ["http://example.com/1", "http://example.com/2", ...]
results = parallel_map(
    download,
    urls,
    n_workers=16,
    mode='thread',
    show_progress=True,
    desc="Downloading files"
)

# CPU-bound: batch computation (multi-processing)
def heavy_compute(x):
    return sum(i**2 for i in range(x))

data = [10000, 20000, 30000, 40000]
results = parallel_map(
    heavy_compute,
    data,
    n_workers=4,
    mode='process',
    show_progress=True
)

# With timeout control
results = parallel_map(
    slow_function,
    items,
    n_workers=8,
    timeout=30.0  # Single task timeout 30 seconds
)
```

**Parameters**:
- `func`: Single-parameter function `func(item) -> result`
- `items`: Input sequence (iterable)
- `n_workers`: Number of concurrent worker threads/processes (default 8)
- `mode`: Concurrency mode
  - `'thread'`: Multi-threading (suitable for I/O-bound tasks like network requests, file I/O)
  - `'process'`: Multi-processing (suitable for CPU-bound tasks like heavy computation)
- `show_progress`: Whether to show tqdm progress bar (default `False`)
- `desc`: Progress bar description text
- `timeout`: Single task timeout in seconds (`None` for unlimited)

**Features**:
- Order preservation: Results order matches input order
- Exception handling: Single task failure throws exception
- Real-time progress: tqdm progress bar support

**Use Cases**:
- Batch file downloads, web scraping
- Batch image processing, video frame extraction
- Batch API calls (Lark, OSS, LLM)

### progress_iter - Wrap with Progress Bar

Wrap any iterable with tqdm progress bar.

```python
from pywayne.tools import progress_iter

# Wrap list
for img_path in progress_iter(image_paths, desc="Loading images"):
    img = load_image(img_path)
    process(img)

# Wrap generator
def data_generator():
    for i in range(1000):
        yield process_data(i)

for result in progress_iter(data_generator(), desc="Processing data", total=1000):
    save(result)

# Custom unit
for file in progress_iter(files, desc="Compressing files", unit="file"):
    compress(file)
```

**Parameters**:
- `iterable`: Input iterable object
- `desc`: Progress bar description text
- `total`: Force specify total count (`None` to auto-infer from `len()`)
- `unit`: Progress bar unit string (default `'it'`)

**Use Cases**:
- Show progress when looping through data
- Progress visualization for generators and iterators

## File Watching

### FileWatcher - File/Directory Watcher (Event-Driven)

Monitor file or directory changes and trigger callbacks. Based on watchdog library, event-driven with low resource usage.

```python
from pywayne.tools import FileWatcher
import time

# ==== Context Manager Usage (Recommended) ====

# Watch for new file creation
def on_new_file(file_path):
    print(f"New file: {file_path}")

with FileWatcher(
    "/data/results",
    on_created=on_new_file,
    extensions=[".csv", ".json"],  # Only watch these extensions
    recursive=True  # Recursively watch subdirectories
):
    time.sleep(3600)  # Watch for 1 hour

# Watch file modifications
def on_modified(file_path):
    print(f"File modified: {file_path}")
    # Reload configuration
    reload_config(file_path)

with FileWatcher(
    "./config.yaml",
    on_modified=on_modified
):
    # Main program logic
    run_server()

# Watch deletion events
def on_deleted(file_path):
    print(f"File deleted: {file_path}")

with FileWatcher(
    "/tmp/watch_dir",
    on_created=on_new_file,
    on_modified=on_modified,
    on_deleted=on_deleted,
    extensions=[".log"]
):
    time.sleep(600)

# ==== Manual Control Usage ====

watcher = FileWatcher(
    "/data/logs",
    on_created=lambda p: print(f"New log: {p}"),
    extensions=[".log"],
    recursive=True
)

watcher.start()  # Start watching (background thread)

# Main program logic
time.sleep(60)

watcher.stop()  # Stop watching

# ==== Combined with Lark Bot ====

from pywayne.lark_custom_bot import LarkCustomBot
bot = LarkCustomBot(webhook_url="...")

def send_alert(file_path):
    bot.send_text_to_chat(f"⚠️ New file detected: {file_path}")

with FileWatcher(
    "/data/results",
    on_created=send_alert,
    extensions=[".csv"],
    recursive=True
):
    time.sleep(86400)  # Watch for 24 hours
```

**Parameters**:
- `path`: File or directory path to watch
- `on_created`: Callback when new file is created `(file_path: str) -> None`
- `on_modified`: Callback when file content is modified `(file_path: str) -> None`
- `on_deleted`: Callback when file is deleted `(file_path: str) -> None`
- `extensions`: Only watch specified extensions (e.g. `['.jpg', '.png']`), empty list watches all files
- `recursive`: Whether to recursively watch subdirectories (only effective when `path` is a directory)

**Methods**:
- `start()`: Start watching (background thread), returns `self` for method chaining
- `stop()`: Stop watching and wait for background thread to exit

**Use Cases**:
- Auto-trigger processing pipeline when data lands
- Auto-push Lark alerts for log anomalies
- Config file hot-reloading (no service restart needed)
- File sync monitoring

## Other Utilities

### compose_funcs - Function Composition (Functional Programming)

Compose multiple functions into a single composite function for chained data processing.

```python
from pywayne.tools import compose_funcs

def add_one(x):
    return x + 1

def multiply_two(x):
    return x * 2

def square(x):
    return x ** 2

# Compose functions: square(multiply_two(add_one(x)))
pipeline = compose_funcs(square, multiply_two, add_one)

print(pipeline(3))  # (3 + 1) * 2 = 8, 8^2 = 64

# Data processing pipeline
def clean_data(data):
    return [x.strip() for x in data]

def to_upper(data):
    return [x.upper() for x in data]

def filter_empty(data):
    return [x for x in data if x]

process_pipeline = compose_funcs(filter_empty, to_upper, clean_data)
result = process_pipeline([" hello ", "world", "  ", "test"])
# Result: ["HELLO", "WORLD", "TEST"]
```

**Use Cases**:
- Data processing pipelines
- Functional programming style
- Chained transformations

### disable_print_wrap_and_suppress - Disable numpy/pandas Wrapping

Disable numpy and pandas automatic line wrapping and scientific notation for full data viewing.

```python
from pywayne.tools import disable_print_wrap_and_suppress
import numpy as np
import pandas as pd

# Enable full display
disable_print_wrap_and_suppress()

# numpy array without wrapping
arr = np.arange(1000)
print(arr)  # Full display, no wrapping

# pandas DataFrame full display
df = pd.DataFrame(np.random.rand(100, 20))
print(df)  # Show all rows and columns

# Only handle numpy
disable_print_wrap_and_suppress(deal_with_pandas=False)

# Only handle pandas
disable_print_wrap_and_suppress(deal_with_numpy=False)
```

**Use Cases**:
- View full data during terminal debugging
- Data display without wrapping
- Avoid scientific notation display

### say - Text-to-Speech

Convert text to speech audio. Uses macOS built-in `say` command on macOS, `espeak-ng` on Linux (auto-installs).

```python
from pywayne.tools import say

# English
say("Hello, world", lang='en')

# Chinese
say("Hello, welcome to pywayne", lang='zh')

# Notification sound
say("Task completed", lang='en')

# Long text
say("This is a long piece of text for testing speech synthesis.", lang='en')
```

**Supported Platforms**:
- **macOS**: Uses built-in `say` command
- **Linux**: Uses `espeak-ng` (auto-installs on first call)

**Use Cases**:
- Task completion audio notifications
- Accessibility applications, assistive reading
- Interactive voice applications

### leader_speech - Generate Corporate Jargon (Entertainment)

Randomly generate corporate meeting-style "leadership speech" text for entertainment.

```python
from pywayne.tools import leader_speech

text = leader_speech()
print(text)
# Example output (Chinese corporate jargon):
# "The underlying logic is to empower the new ecosystem and implement industry closed-loop..."
```

**Use Cases**:
- Entertainment, demonstrations
- Testing text processing functions

## Complete Import Statement

```python
from pywayne.tools import (
    # Decorators
    func_timer,             # Single function timing
    func_timer_batch,       # Batch function timing statistics
    trace_calls,            # Function call tracing
    maximize_figure,        # Maximize matplotlib window
    binding_press_release,  # Bind mouse/keyboard events
    singleton,              # Singleton pattern
    retry,                  # Automatic retry with exponential backoff
    disk_cache,             # Disk cache with persistence
    with_progress,          # Auto-add progress bar
    
    # File Operations
    list_all_files,         # Recursive file listing with filtering
    count_file_lines,       # Fast file line counting
    
    # Logging and Printing
    wayne_logger,           # Colored logger
    wayne_print,            # Enhanced colored print with multi-level debug
    wayne_print_table,      # Formatted table printing
    
    # Config Files
    write_yaml_config,      # Write YAML config with update and lock support
    read_yaml_config,       # Read YAML config with lock support
    
    # Concurrency & Parallelism
    parallel_map,           # Concurrent mapping with order preservation
    progress_iter,          # Wrap with progress bar
    
    # File Watching
    FileWatcher,            # File/directory watcher (event-driven)
    
    # Other Utilities
    compose_funcs,                      # Function composition
    disable_print_wrap_and_suppress,    # Disable numpy/pandas wrapping
    say,                                # Text-to-speech
    leader_speech,                      # Generate corporate jargon
)
```

## Dependencies

### Required Dependencies

```
matplotlib>=3.0.0       # For @maximize_figure, @binding_press_release
pyyaml>=5.0            # For YAML config read/write
filelock>=3.0.0        # For file lock protection (multi-process safe)
Pillow>=8.0.0          # PIL support
tqdm>=4.50.0           # Progress bar display
watchdog>=2.0.0        # File watching (FileWatcher)
```

### Optional Dependencies

```
espeak-ng              # Text-to-speech on Linux (say function)
                       # macOS has built-in say command, no installation needed
```

## Installation

```bash
# Install pywayne (includes all dependencies)
pip install pywayne

# Or install from source
git clone https://github.com/Wayne-sketch/wayne_algorithm_lib.git
cd wayne_algorithm_lib
pip install -e .
```

## Quick Reference Index

### Performance Analysis
- `@func_timer` - Single timing
- `@func_timer_batch` - Batch timing statistics
- `@trace_calls` - Call tracing

### Network/IO Reliability
- `@retry` - Automatic retry (network requests, file operations)
- `@disk_cache` - Result caching (LLM, slow queries)

### Concurrent Processing
- `parallel_map` - Batch concurrency (downloads, API calls)
- `progress_iter` - Progress visualization
- `@with_progress` - Auto progress bar

### Debugging & Monitoring
- `wayne_print(verbose=1/2)` - Multi-level debug output
- `wayne_print_table` - Table beautification
- `FileWatcher` - File change monitoring

### Config Management
- `read_yaml_config(use_lock=True)` - Multi-process safe reading
- `write_yaml_config(update=True, use_lock=True)` - Safe updates

### Design Patterns
- `@singleton` - Singleton pattern
- `compose_funcs` - Function composition pipeline

## Common Usage Scenarios

### Scenario 1: Batch API Calls with Retry and Cache

```python
from pywayne.tools import retry, disk_cache, parallel_map

@retry(max_tries=3, delay=1.0, backoff=2.0)
@disk_cache(ttl=3600)
def call_api(url):
    # API call logic
    pass

urls = [...]
results = parallel_map(call_api, urls, n_workers=16, show_progress=True)
```

### Scenario 2: Data Processing Pipeline with Progress Bar

```python
from pywayne.tools import progress_iter, wayne_print

def process_pipeline(files):
    for file in progress_iter(files, desc="Processing files"):
        data = load(file)
        result = transform(data)
        save(result)
    wayne_print("Processing complete!", color="green", bold=True)
```

### Scenario 3: File Watching + Lark Bot Notifications

```python
from pywayne.tools import FileWatcher
from pywayne.lark_custom_bot import LarkCustomBot

bot = LarkCustomBot(webhook_url="...")

def alert(file_path):
    bot.send_text_to_chat(f"🔔 New file: {file_path}")

with FileWatcher("/data", on_created=alert, extensions=[".csv"], recursive=True):
    while True:
        time.sleep(60)
```

### Scenario 4: Debug Complex Issues with Full Call Stack

```python
from pywayne.tools import wayne_print

def debug_function():
    data = {"key": "value", "nested": {"a": 1, "b": 2}}
    wayne_print(data, color="yellow", verbose=2)  # Show full call stack
```

## Important Notes

1. **Prefer pywayne built-in tools**: Avoid reinventing the wheel or adding new dependencies
2. **Use file locks in multi-process scenarios**: `read_yaml_config(use_lock=True)` and `write_yaml_config(use_lock=True)`
3. **Use thread for I/O-bound, process for CPU-bound**: `parallel_map(mode='thread'/'process')`
4. **Retry decorator order**: `@retry` should be outside `@disk_cache` to ensure retries before caching
5. **FileWatcher is lightweight**: Event-driven, low resource usage, suitable for long-running tasks
