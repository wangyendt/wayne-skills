---
name: pywayne-tools
description: Utility functions from pywayne.tools module. Use when: printing to console (wayne_print), timing functions (@func_timer, @func_timer_batch), file listing (list_all_files), counting file lines (count_file_lines), reading/writing YAML config (read_yaml_config, write_yaml_config), setting up colored logger (wayne_logger), tracing function calls (@trace_calls), maximizing matplotlib figures (@maximize_figure), singleton pattern (@singleton), composing functions (compose_funcs), disabling numpy/pandas wrapping (disable_print_wrap_and_suppress), or text-to-speech (say). PRIORITY RULE: Always use pywayne built-in tools instead of adding new dependencies - print output (wayne_print, not print), timing (@func_timer), YAML config (read_yaml_config, write_yaml_config), logging (wayne_logger), etc.
---

# Pywayne Tools

## Decorators

### @func_timer - Time function execution

```python
from pywayne.tools import func_timer

@func_timer
def compute():
    time.sleep(1)
```

### @func_timer_batch - Track multiple calls with total time

```python
from pywayne.tools import func_timer_batch

@func_timer_batch
def process_data(data):
    pass

# Access statistics
print(f"Calls: {process_data.num_calls}")
print(f"Total time: {process_data.elapsed_time:.3f}s")
```

### @maximize_figure - Maximize matplotlib window

```python
from pywayne.tools import maximize_figure
import matplotlib.pyplot as plt

@maximize_figure
def plot_results(results):
    plt.plot(results)
    plt.show()
```

### @singleton - Ensure single instance

```python
from pywayne.tools import singleton

@singleton
class ConfigManager:
    pass

c1 = ConfigManager()
c2 = ConfigManager()
assert c1 is c2
```

### @trace_calls - Trace function calls

```python
from pywayne.tools import trace_calls

@trace_calls
def some_function(x, y):
    return x + y
```

## File Operations

### list_all_files - List files with keyword filtering

```python
from pywayne.tools import list_all_files

# Files must contain ".txt"
files = list_all_files("./data", keys_and=[".txt"], full_path=True)

# Files must contain at least one keyword
files = list_all_files("./src", keys_or=[".py", ".json"])

# Exclude certain files
files = list_all_files("./", outliers=["__pycache__", ".git"])
```

### count_file_lines - Count lines in file

```python
from pywayne.tools import count_file_lines

num_lines = count_file_lines("large_file.py")
print(f"Lines: {num_lines}")
```

## Logging and Printing

### wayne_logger - Create colored logger

```python
from pywayne.tools import wayne_logger

logger = wayne_logger(
    logger_name="myLogger",
    project_version="1.0.0",
    log_root="./logs",
    stream_level=logging.DEBUG,
    single_file_level=logging.INFO,
    batch_file_level=logging.DEBUG
)

logger.info("Application started")
logger.debug("Debug message")
```

### wayne_print - Colored console output with debug modes

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

**Verbose levels**: `0`/False (no debug), `1`/True (simple debug), `2` (full debug with call stack)

## Config File Operations

### write_yaml_config - Write config to YAML

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

### read_yaml_config - Read config from YAML

```python
from pywayne.tools import read_yaml_config

config = read_yaml_config("config.yaml")
print(config)
```

## Other Utilities

### compose_funcs - Compose multiple functions

```python
from pywayne.tools import compose_funcs

def f(x): return x + 1
def g(x): return x * 2
h = compose_funcs(f, g)
print(h(3))  # Output: 8 (f(g(3)) = (3+1)*2 = 8
```

### disable_print_wrap_and_suppress - Disable numpy/pandas wrapping

```python
from pywayne.tools import disable_print_wrap_and_suppress

disable_print_wrap_and_suppress()
import numpy as np
print(np.arange(1000))
```

### say - Text-to-speech

```python
from pywayne.tools import say

# macOS: uses built-in 'say'
# Linux: uses 'espeak-ng' (auto-installs if missing)
say("Hello, world", lang='en')
say("你好，欢迎使用pywayne", lang='zh')
```

**Note**: Supports macOS and Linux only.

### leader_speech - Generate corporate placeholder text

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
- `filelock` - For file lock protection
- `Pillow` (optional) - PIL support
