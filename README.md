# HC Toolbox

A collection of utility tools for various tasks.

- [HC Toolbox](#hc-toolbox)
  - [Tools](#tools)
    - [Naming Checker](#naming-checker)
    - [Video Frame Extractor](#video-frame-extractor)

## Tools

### Naming Checker

Validates file and folder names against a regex pattern. Useful for enforcing naming conventions across a directory structure.

**Features:**
- Validate names against custom regex patterns
- Support for ignore patterns (gitignore-style)
- Save results to a file
- GUI mode available

**Usage:**
```bash
cd naming_checker
python naming_checker.py <path> [-r REGEX] [-i IGNORE_FILE] [-o OUTPUT_DIR] [--gui]
```

**Example:**
```bash
python naming_checker.py /path/to/check -r "^[a-z0-9_]+$" --gui
```

**Installation:**
```bash
cd naming_checker
pip install -r requirements.txt
```

### Video Frame Extractor

Extracts frames from video files with various options for customization.

**Features:**
- Extract frames at specified intervals
- Resize frames with different interpolation methods
- Extract specific frame ranges
- Show video information
- GUI mode available

**Usage:**
```bash
cd video_frame_extractor
python video_frame_extractor.py <video> [-o OUTPUT_DIR] [-i INTERVAL] [--scale SCALE] [--interpolation METHOD] [-s START] [-e END] [--info] [--gui]
```

**Examples:**
```bash
# Extract every frame
python video_frame_extractor.py video.mp4

# Extract every 10th frame
python video_frame_extractor.py video.mp4 -i 10

# Extract frames with 2x scaling
python video_frame_extractor.py video.mp4 --scale 2.0

# Show video information
python video_frame_extractor.py video.mp4 --info

# Use GUI mode
python video_frame_extractor.py video.mp4 --gui
```

**Installation:**
```bash
cd video_frame_extractor
pip install -r requirements.txt
```
