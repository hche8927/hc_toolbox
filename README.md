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
- Support for ignore patterns (gitignore-style) via `.ignore` file
- Automatically skips hidden files (starting with `.`) and common special files
- Save results to a file
- Cross-platform support (Windows, Mac, Linux)
- GUI mode available

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

**Ignore Patterns:**
The checker uses a `.ignore` file (similar to `.gitignore`) to skip files and directories that shouldn't be checked. By default, it looks for `.ignore` in the current directory or the target directory. The default `.ignore` file includes:
- Hidden files and directories (starting with `.`)
- Common special files (README, LICENSE, CHANGELOG, etc.)
- Documentation files (*.md, *.txt, *.rst)
- Build directories (node_modules, __pycache__, build, etc.)
- IDE files (.vscode, .idea, .DS_Store, etc.)
- Cloud drive directories (OneDrive, iCloud Drive, Google Drive, Dropbox, Box, etc.)

You can customize the `.ignore` file to match your needs. To avoid checking cloud drives or other directories, add patterns like `OneDrive/`, `iCloud Drive/`, etc. to your `.ignore` file.

### Naming Normalizer

Normalizes file and folder names to a standard format (lowercase with underscores). Useful for cleaning up inconsistent naming across a directory structure.

**Features:**
- Normalize names to lowercase with underscores
- Preserves names in non-Latin scripts (Chinese, Japanese, Korean, Russian, Hebrew, Arabic, etc.)
- Normalizes accented Latin characters (é → e, ñ → n, etc.)
- Support for ignore patterns (gitignore-style) via `.ignore` file
- Automatically skips hidden files (starting with `.`) and common special files (README, LICENSE, etc.)
- Nested rename toggle (default: off, only processes root level)
- Dry run mode (default: on, shows what would be renamed without making changes)
- Confirm option (requires both `--no-dry-run` and `--confirm` to actually rename)
- Handles case-insensitive filesystems (Mac/Windows) correctly
- Detects and warns about naming conflicts
- Cross-platform support (Windows, Mac, Linux)
- GUI mode available

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

**Ignore Patterns:**
The normalizer uses a `.ignore` file (similar to `.gitignore`) to skip files and directories that shouldn't be renamed. By default, it looks for `.ignore` in the current directory or the target directory. The default `.ignore` file includes:
- Hidden files and directories (starting with `.`)
- Common special files (README, LICENSE, CHANGELOG, etc.)
- Documentation files (*.md, *.txt, *.rst)
- Build directories (node_modules, __pycache__, build, etc.)
- IDE files (.vscode, .idea, .DS_Store, etc.)
- Cloud drive directories (OneDrive, iCloud Drive, Google Drive, Dropbox, Box, etc.)

You can customize the `.ignore` file to match your needs. To avoid processing cloud drives, add patterns like `OneDrive/`, `iCloud Drive/`, etc. to your `.ignore` file.

**International Character Support:**
The normalizer automatically preserves file and directory names containing non-Latin scripts to prevent corruption of international file names. Names in the following scripts are preserved as-is:
- Chinese (Simplified and Traditional)
- Japanese (Hiragana, Katakana, Kanji)
- Korean (Hangul)
- Russian and other Cyrillic scripts
- Hebrew
- Arabic
- Thai, Hindi, and other scripts

Accented Latin characters (like café, résumé, naïve) are normalized to their ASCII equivalents (cafe, resume, naive).

### Video Frame Extractor

Extracts frames from video files with various options for customization.

**Features:**
- Extract frames at specified intervals
- Resize frames with different interpolation methods (nearest, linear, cubic, area, lanczos4)
- Extract specific frame ranges
- Show video information
- Cross-platform support (Windows, Mac, Linux)
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

# Extract frames with custom interpolation method
python video_frame_extractor.py video.mp4 --interpolation cubic

# Extract specific frame range
python video_frame_extractor.py video.mp4 -s 100 -e 500

# Show video information
python video_frame_extractor.py video.mp4 --info

# Use GUI mode
python video_frame_extractor.py video.mp4 --gui
```
