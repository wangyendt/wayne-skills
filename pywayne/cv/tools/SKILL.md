---
name: pywayne-cv-tools
description: OpenCV YAML file read/write utilities. Use when working with pywayne.cv.tools module to read OpenCV FileStorage YAML files with support for nested structures, numpy arrays, basic types, and lists. Handles cv2.FileNode parsing including Map, Seq, and matrix nodes.
---

# Pywayne CV YAML I/O

This module provides utilities for reading and writing OpenCV `cv2.FileStorage` YAML files.

## Quick Start

```python
from pywayne.cv.tools import read_cv_yaml, write_cv_yaml
import numpy as np

# Write to YAML file
data = {
    "camera_name": "test_camera",
    "image_width": 1920,
    "image_height": 1080,
    "calibration_matrix": np.eye(3)
}
write_cv_yaml('config.yaml', data)

# Read from YAML file
data = read_cv_yaml('config.yaml')
print(data)
```

## Supported Data Types

| Type | Handling |
|------|---------|
| `int`, `float`, `str` | Written directly |
| `np.ndarray` | Written using `fs.write()` |
| `list` | Written using `FileNode_SEQ` |
| `dict` | Written using `FileNode_MAP` |
| `None` | Skipped |

## Reading Files

```python
from pywayne.cv.tools import read_cv_yaml

# Read YAML file (returns dict or None on error)
data = read_cv_yaml('camera_config.yaml')
if data:
    print(data['camera_name'])
    print(data['image_width'])
```

**Notes:**
- Handles nested structures recursively
- Returns `None` if file cannot be opened
- Uses `wayne_print` for error messages (red/yellow colors)
- Supports both `FileNode_MAP` and `FileNode_SEQ` for dictionaries and lists
- Matrix nodes read using `.mat()` method

## Writing Files

```python
from pywayne.cv.tools import write_cv_yaml

# Write data to YAML file
data = {
    "matrix": np.eye(3),
    "vector": [1, 2, 3]
}
success = write_cv_yaml('config.yaml', data)

if success:
    print("Write successful")
```

**Notes:**
- Returns `True` on success, `False` on error
- Handles lists with empty key convention for OpenCV
- Supports unnamed sequences using empty key string
- Skips `None` values during write

## Requirements

- `cv2` (OpenCV) - For FileStorage operations
- `numpy` - For numpy array handling
- `pywayne.tools` - For wayne_print logging

## API Reference

| Function | Description |
|---------|-------------|
| `read_cv_yaml(path)` | Read OpenCV YAML file, returns dict or None |
| `write_cv_yaml(path, data)` | Write dict to OpenCV YAML file, returns bool |

## File Structure Handling

The module handles OpenCV's `cv2.FileNode` types:

| Node Type | Handling |
|-----------|---------|
| Map | Uses `.keys()` method (requires callable) |
| Seq | Uses element iteration with recursive parsing |
| Matrix | Uses `.mat()` method |
| Int/Float/String | Uses `.real()`, `.int()`, `.string()` methods |
