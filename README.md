# HC Toolbox

A collection of utility tools for file management and video processing.

## Installation

```bash
# Install all dependencies
pip install Gooey>=1.0.0 opencv-python>=4.8.0 numpy>=1.21.0

# Or install per tool
cd naming_checker && pip install -r requirements.txt
cd naming_normalizer && pip install -r requirements.txt
cd video_frame_extractor && pip install -r requirements.txt
```

## Tools

### Naming Checker

Validates file and folder names against a regex pattern. Useful for enforcing naming conventions across a directory structure.

**Usage:**
```bash
cd naming_checker
python naming_checker.py <path> [-r REGEX] [-i IGNORE_FILE] [-o OUTPUT_DIR] [--gui]
```

**Examples:**
```bash
# Check with default pattern (lowercase alphanumeric and underscores)
python naming_checker.py /path/to/check

# Check with custom regex pattern
python naming_checker.py /path/to/check -r "^[a-z0-9_]+$"

# Use custom ignore file
python naming_checker.py /path/to/check -i /path/to/.ignore

# Save results to custom output directory
python naming_checker.py /path/to/check -o /path/to/output

# Use GUI mode
python naming_checker.py /path/to/check --gui
```

**Features:**
- Validate names against custom regex patterns
- Gitignore-style ignore patterns (automatically finds `.ignore` in tool directory)
- Automatically skips hidden files and common special files
- Saves invalid paths to a timestamped file in Downloads (or custom output directory)
- Cross-platform support (Windows, Mac, Linux)
- GUI mode available

**Ignore Patterns:**
The checker uses a `.ignore` file (similar to `.gitignore`) to skip files and directories. By default, it automatically finds `.ignore` in the tool's directory, or you can specify a custom path. The default `.ignore` includes hidden files, documentation files, build directories, IDE files, and cloud drive directories.

### Naming Normalizer

Normalizes file and folder names to a standard format (lowercase with underscores). Useful for cleaning up inconsistent naming across a directory structure.

**Usage:**
```bash
cd naming_normalizer
python naming_normalizer.py <path> [-n] [--no-dry-run] [--confirm] [-i IGNORE_FILE] [--gui]
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

# Use custom ignore file
python naming_normalizer.py /path/to/normalize -i /path/to/.ignore

# Use GUI mode
python naming_normalizer.py /path/to/normalize --gui
```

**Features:**
- Normalize names to lowercase with underscores
- Preserves names in non-Latin scripts (Chinese, Japanese, Korean, Russian, Hebrew, Arabic, etc.)
- Normalizes accented Latin characters (é → e, ñ → n, etc.)
- Gitignore-style ignore patterns (automatically finds `.ignore` in tool directory)
- Automatically skips hidden files and common special files (README, LICENSE, etc.)
- Nested rename toggle (default: off, only processes root level)
- Dry run mode (default: on, shows what would be renamed without making changes)
- Confirm option (requires both `--no-dry-run` and `--confirm` to actually rename)
- Handles case-insensitive filesystems (Mac/Windows) correctly
- Detects and warns about naming conflicts
- Cross-platform support (Windows, Mac, Linux)
- GUI mode available

**Ignore Patterns:**
The normalizer uses a `.ignore` file (similar to `.gitignore`) to skip files and directories. By default, it automatically finds `.ignore` in the tool's directory, or you can specify a custom path. The default `.ignore` includes hidden files, documentation files, build directories, IDE files, and cloud drive directories.

**International Character Support:**
The normalizer automatically preserves file and directory names containing non-Latin scripts to prevent corruption. Names in Chinese, Japanese, Korean, Russian, Hebrew, Arabic, Thai, Hindi, and other scripts are preserved as-is. Accented Latin characters (like café, résumé, naïve) are normalized to their ASCII equivalents (cafe, resume, naive).

### Video Frame Extractor

Extracts frames from video files with various options for customization.

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

# Extract frames with custom interpolation method
python video_frame_extractor.py video.mp4 --interpolation cubic

# Extract specific frame range
python video_frame_extractor.py video.mp4 -s 100 -e 500

# Show video information
python video_frame_extractor.py video.mp4 --info

# Use GUI mode
python video_frame_extractor.py video.mp4 --gui
```

**Features:**
- Extract frames at specified intervals
- Resize frames with different interpolation methods (nearest, linear, cubic, area, lanczos4)
- Extract specific frame ranges
- Show video information (resolution, FPS, duration, frame count)
- Outputs frames as PNG files
- Default output directory: Downloads/frames
- Cross-platform support (Windows, Mac, Linux)
- GUI mode available
