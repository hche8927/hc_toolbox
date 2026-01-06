# HC Toolbox

A collection of utility tools for various tasks.

- [HC Toolbox](#hc-toolbox)
  - [Installation](#installation)
    - [Install All Tools](#install-all-tools)
    - [Install Individual Tools](#install-individual-tools)
  - [Tools](#tools)
    - [Naming Checker](#naming-checker)
    - [Naming Normalizer](#naming-normalizer)
    - [Video Frame Extractor](#video-frame-extractor)

## Installation

### Install All Tools

To install dependencies for all tools at once:

```bash
# Install all dependencies
pip install Gooey>=1.0.0 opencv-python>=4.8.0 numpy>=1.21.0
```

### Install Individual Tools

Alternatively, you can install dependencies for each tool individually:

```bash
# Naming Checker
cd naming_checker
pip install -r requirements.txt

# Naming Normalizer
cd naming_normalizer
pip install -r requirements.txt

# Video Frame Extractor
cd video_frame_extractor
pip install -r requirements.txt
```

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

### Naming Normalizer

Normalizes file and folder names to a standard format (lowercase with underscores). Useful for cleaning up inconsistent naming across a directory structure.

**Features:**
- Normalize names to lowercase with underscores
- Nested rename toggle (default: off, only processes root level)
- Dry run mode (default: on, shows what would be renamed without making changes)
- Confirm option (requires both --no-dry-run and --confirm to actually rename)
- GUI mode available

**Usage:**
```bash
cd naming_normalizer
python naming_normalizer.py <path> [-n] [--no-dry-run] [--confirm] [--gui]
```

**Examples:**
```bash
# Dry run (default) - see what would be renamed
python naming_normalizer.py /path/to/normalize

# Show what would be renamed (no dry run, but not confirmed)
python naming_normalizer.py /path/to/normalize --no-dry-run

# Actually perform the renames (requires both --no-dry-run and --confirm)
python naming_normalizer.py /path/to/normalize --no-dry-run --confirm

# Process subdirectories recursively and rename
python naming_normalizer.py /path/to/normalize -n --no-dry-run --confirm

# Use GUI mode
python naming_normalizer.py /path/to/normalize --gui
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
