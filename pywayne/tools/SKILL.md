---
name: pywayne-tools
description: Collection of Python utility decorators and helper functions from pywayne.tools module. Use when users need: (1) Function execution timing and profiling (@func_timer, @func_timer_batch), (2) Colored console output with debug modes (wayne_print), (3) File operations (list_all_files, count_file_lines), (4) YAML config read/write (read_yaml_config, write_yaml_config), (5) Logger setup with colored output (wayne_logger), (6) Function call tracing (@trace_calls), or (7) Other utilities like @singleton, @maximize_figure, compose_funcs, say().
---

# Pywayne Tools

Utility decorators and helper functions from `pywayne.tools` module.

## Quick Start

```python
# Color output
from pywayne.tools import wayne_print
wayne_print("Success", color="green")

# Function timing
from pywayne.tools import func_timer

@func_timer
def my_function():
    time.sleep(1)
```

## Decorators

### @func_timer

Measure single function execution time.

```python
from pywayne.tools import func_timer

@func_timer
def compute():
    # Heavy computation
    pass
```

**Use case**: Performance tuning, monitoring critical functions.

### @func_timer_batch

Track multiple function calls with total elapsed time.

```python
from pywayne.tools import func_timer_batch

@func_timer_batch
def process_data(data):
    # Batch processing
    pass

# Get statistics
print(f"Calls: {process_data.num_calls}")
print(f"Total time: {process_data.elapsed_time:.3f}s")
```

**Use case**: Batch processing, repeated function calls performance analysis.

### @maximize_figure

Maximize matplotlib figure window automatically.

```python
from pywayne.tools import maximize_figure
import matplotlib.pyplot as plt

@maximize_figure
def plot_results(results):
    plt.plot(results)
    plt.show()
```

**Use case**: Full-screen presentations, matplotlib visualization.

### @singleton

Ensure a class is instantiated only once.

```python
from pywayne.tools import singleton

@singleton
class ConfigManager:
    pass

# Both calls return same instance
c1 = ConfigManager()
c2 = ConfigManager()
assert c1 is c2  # True
```

**Use case**: Database connections, config managers, shared resources.

### @trace_calls

Trace function calls with detailed logging. Supports `print_type='default'` or `print_type='pprint'`.

```python
from pywayne.tools import trace_calls

@trace_calls
def some_function(x, y):
    return x + y
```

**Use case**: Debugging complex systems, understanding call relationships.

## File Operations

### list_all_files

List files in directory with keyword filtering.

```python
from pywayne.tools import list_all_files

# All files with ".txt" in name
files = list_all_files("./data", keys_and=[".txt"], full_path=True)

# Files with at least one keyword
files = list_all_files("./src", keys_or=[".py", ".json"])

# Exclude certain files
files = list_all_files("./", outliers=["__pycache__", ".git"])
```

**Parameters**:
- `root`: Root directory to search
- `keys_and`: Files must contain ALL these keywords
- `keys_or`: Files must contain AT LEAST ONE of these keywords
- `outliers`: Files must NOT contain these keywords
- `full_path`: Return full paths if True

### count_file_lines

Count lines in a file efficiently (block-based reading for large files).

```python
from pywayne.tools import count_file_lines

num_lines = count_file_lines("large_file.py")
print(f"Lines: {num_lines}")
```

## Logging and Printing

### wayne_logger

Create colored logger with console and file output.

```python
from pywayne.tools import wayne_logger

logger = wayne_logger(
    logger_name="myLogger",
    project_version="1.0.0",
    log_root="./logs",
    stream_level=logging.DEBUG,      # Console level
    single_file_level=logging.INFO,  # main.log level
    batch_file_level=logging.DEBUG  # batch log level
)

logger.info("Application started")
logger.debug("Debug message")
```

**Output files**:
- `./logs/main.log` - Single rolling log file
- `./logs/batches/{version}_{timestamp}.log` - Batch log files

### wayne_print

Colored console output with multi-level debug mode.

```python
from pywayne.tools import wayne_print

# Basic usage
wayne_print("Success", color="green")
wayne_print("Error", color="red", bold=True)

# Verbose mode 1: timestamp + file + line
wayne_print("Debug info", color="yellow", verbose=1)

# Verbose mode 2: full call stack
wayne_print("Detailed debug", color="red", verbose=2)
```

**Colors**: `default`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`

**Verbose levels**:
- `0` or `False`: No debug (default)
- `1` or `True`: Simple debug (timestamp + file + line)
- `2`: Full debug (complete call stack)

**Auto-pprint**: Complex data types (dict, list, tuple, set) are automatically formatted with pprint.

## Config File Operations

### write_yaml_config

Write config dictionary to YAML file with file lock protection.

```python
from pywayne.tools import write_yaml_config

config = {'version': '1.0.0', 'debug': True}

# Overwrite file
write_yaml_config("config.yaml", config)

# Update existing file (deep merge)
write_yaml_config("config.yaml", config, update=True)

# With file lock (default is False)
write_yaml_config("config.yaml", config, use_lock=True)
```

### read_yaml_config

Read config from YAML file with file lock protection.

```python
from pywayne.tools import read_yaml_config

config = read_yaml_config("config.yaml")
print(config)
```

## Other Utilities

### compose_funcs

Compose multiple functions into one.

```python
from pywayne.tools import compose_funcs

def f(x): return x + 1
def g(x): return x * 2
h = compose_funcs(f, g)
print(h(3))  # Output: 8 (f(g(3)) = (3+1)*2 = 8)
```

### disable_print_wrap_and_suppress

Disable numpy/pandas line wrapping and scientific notation.

```python
from pywayne.tools import disable_print_wrap_and_suppress

disable_print_wrap_and_suppress()
import numpy as np
print(np.arange(1000))  # Now prints without wrapping
```

### say

Text-to-speech using system TTS engine.

```python
from pywayne.tools import say

# macOS: uses built-in 'say'
# Linux: uses 'espeak-ng' (auto-installs if missing)
say("Hello, world", lang='en')
say("你好，欢迎使用pywayne", lang='zh')
```

**Note**: Supports macOS and Linux only. Raises `NotImplementedError` on Windows.

### leader_speech

Generate corporate-style placeholder text (for fun/testing).

```python
from pywayne.tools import leader_speech

text = leader_speech()
print(text)
```

## Import Statement

```python
from pywayne.tools import (
    func_timer,
    func_timer_batch,
    maximize_figure,
    singleton,
    trace_calls,
    list_all_files,
    count_file_lines,
    wayne_logger,
    wayne_print,
    write_yaml_config,
    read_yaml_config,
    compose_funcs,
    disable_print_wrap_and_suppress,
    say,
    leader_speech
)
```

## Dependencies

- `matplotlib` - For @maximize_figure
- `yaml` - For config operations
- `filelock` - For file lock protection in config ops
- `Pillow` (optional) - PIL support
