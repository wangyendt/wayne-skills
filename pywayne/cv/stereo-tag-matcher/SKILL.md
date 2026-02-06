---
name: pywayne-cv-stereo-tag-matcher
description: Stereo vision AprilTag matching for dual-camera systems. Use when working with pywayne.cv.stereo_tag_matcher module to match AprilTags from left/right camera views, find common tags between images, stitch stereo images together, and visualize results with color-coded annotations (all tags green, common tags yellow, red connection lines).
---

# Pywayne Stereo Tag Matcher

This module matches AprilTags detected in stereo camera pairs.

## Quick Start

```python
from pywayne.cv.stereo_tag_matcher import StereoTagMatcher
from pathlib import Path

# Initialize matcher with custom colors
matcher = StereoTagMatcher(
    target_height=600,
    line_color=(0, 0, 255),  # Red
    all_tag_color=(0, 255, 0),  # Green
    common_tag_color=(0, 255, 255)  # Yellow
)

# Process stereo pair
left_img = Path('left.png')
right_img = Path('right.png')
matched_info, stitched = matcher.process_pair(left_img, right_img, show=True)

# Save result
if stitched is not None:
    import cv2
    cv2.imwrite('stereo_result.png', stitched)
```

## Initialization

```python
matcher = StereoTagMatcher(
    target_height=600,      # Fixed height for resizing
    line_color=(0, 0, 255),   # Custom line color (BGR)
    line_thickness=2,
    box_thickness=2,
    all_tag_color=(0, 255, 0),
    common_tag_color=(0, 255, 255)
)
```

## Input

| Parameter | Type | Description |
|-----------|------|-------------|
| `image1_input` | str, Path, or np.ndarray | Left camera image |
| `image2_input` | str, Path, or np.ndarray | Right camera image |
| `show` | bool | Display stitched result with cv2.imshow |

## Output

### Returned Dictionary

```python
{
    "tag_id": {
        "cam1_center": (x, y),      # Left image center
        "cam1_corners": [(x1, y1), ...], # Left image corners
        "cam2_center": (x, y),      # Right image center
        "cam2_corners": [(x1, y1), ...]  # Right image corners
    },
    ...
}
```

Only tags found in both images are included in the output.

## Visualization

The stitched image displays:

- **All tags** - Green boxes (BGR: 0, 255, 0)
- **Common tags** - Yellow boxes (BGR: 0, 255, 255)
- **Connection lines** - Red lines connecting common tag centers (BGR: 0, 0, 255)

## Use Cases

- Stereo camera calibration - Match common tags to calibrate stereo cameras
- Robot vision - Identify shared landmarks for navigation
- Augmented reality - Track common fiducial markers

## Requirements

- `cv2` (OpenCV) - Image processing and display
- `numpy` - Array operations
- `pywayne.cv.apriltag_detector` - AprilTag detection

## Notes

- Images are resized to `target_height` for consistent annotation
- Tag coordinates are scaled proportionally based on image dimensions
- Supports both grayscale and BGR color input images
