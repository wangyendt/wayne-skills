---
name: pywayne-cv-apriltag-detector
description: AprilTag corner detection for camera calibration and pose estimation. Use when working with pywayne.cv.apriltag_detector module to detect AprilTag fiducial markers in images, extract tag IDs and four corner coordinates, choose tag families such as tag16h5 or tag36h11, apply optional preprocessing, and rely on automatic apriltag_detection installation via gettool.
---

# Pywayne AprilTag Detector

This module detects AprilTag fiducial markers for camera calibration and pose estimation.

## Quick Start

```python
from pywayne.cv.apriltag_detector import ApriltagCornerDetector

# Create detector. Default tag family is 36h11.
detector = ApriltagCornerDetector(tag_family="36h11")

# Detect from file path
detections = detector.detect('test.png', show_result=True)

# Detect from numpy array
import cv2
image = cv2.imread('test.png')
detections = detector.detect(image)
```

## Corner Extraction Task Pattern

When the user asks to detect AprilTag corners in an image, produce IDs and corner coordinates directly. Prefer non-GUI code unless the user asks for visualization.

```python
from pywayne.cv.apriltag_detector import ApriltagCornerDetector

detector = ApriltagCornerDetector(
    tag_family="36h11",
    preprocess=None,  # or "norm", "clahe", "equalize", "norm-clahe"
)
detections = detector.detect("image.jpg")

for det in detections:
    print({
        "id": det.id,
        "hamming_distance": det.hamming_distance,
        "center": tuple(det.center),
        "corners": [tuple(p) for p in det.corners],
    })
```

If detection is poor because of lighting or contrast, retry with `preprocess="norm-clahe"` or `preprocess="clahe"` before changing algorithm parameters.

## Detection Methods

### detect()

Detect AprilTags in an image:

```python
detections = detector.detect(
    image,           # File path, Path object, or numpy array
    show_result=False, # Show visualization window
    preprocess=None    # Optional override for this call
)
```

Returns list of detection results with:
- `id`: Tag ID
- `hamming_distance`: Detection confidence
- `center`: Tag center coordinates (x, y)
- `corners`: 4 corner coordinates

### detect_and_draw()

Detect AprilTags and draw results on original image:

```python
result_image = detector.detect_and_draw(image)
cv2.imshow('Detection Result', result_image)
cv2.waitKey(0)
```

Visualization includes:
- Green polygon outlines
- Red corner circles
- Red ID labels at tag centers

## Requirements

- `cv2` (OpenCV) - Image processing
- `numpy` - Array operations
- `gettool` - Downloads apriltag_detection library automatically

## Library Installation

The detector automatically checks for and installs the `apriltag_detection` library using `gettool` if not found. The pywayne wrapper uses a shared C++ module loader that distinguishes a missing module from a local extension that exists but fails to load because of missing runtime libraries or ABI mismatch.

If installation fails while cloning from GitHub, check for sandbox/proxy restrictions before blaming the user's proxy. Useful checks:

```bash
git config --global --get http.proxy
git config --global --get https.proxy
lsof -nP -iTCP:7890 -sTCP:LISTEN
nc -vz 127.0.0.1 7890
curl -I --proxy http://127.0.0.1:7890 https://github.com --connect-timeout 5
```

In Codex, if `nc` or `curl` fails with `Operation not permitted` or cannot reach `127.0.0.1:7890` inside the sandbox, rerun the essential check or `gettool apriltag_detection -b` with `sandbox_permissions: "require_escalated"` and a short justification.

## Tag Families And Preprocessing

Supported tag families:

- `16h5` / `tag16h5`
- `25h7` / `tag25h7`
- `25h9` / `tag25h9`
- `36h9` / `tag36h9`
- `36h11` / `tag36h11` (default)

Supported preprocessing modes:

- `None` (default)
- `"norm"` or `"normalize"`
- `"clahe"`
- `"equalize"` / `"hist"` / `"eq"`
- `"norm-clahe"`
- A sequence such as `["norm", "clahe"]`

## Detection Result Format

Each detection contains:

| Field | Description |
|--------|-------------|
| `id` | Tag identifier |
| `hamming_distance` | Hamming distance (lower = more confident) |
| `center` | Tag center as (x, y) tuple |
| `corners` | 4 corner coordinates as [(x1, y1), (x2, y2), (x3, y3), (x4, y4)] |

## Notes

- Supports both grayscale and BGR images
- Automatic grayscale conversion for detection
- Visualization sizes scale with image dimensions
- Uses AprilTag 36h11 tag family by default
- For calibration-board photos under uneven illumination, try `preprocess="norm-clahe"` first
