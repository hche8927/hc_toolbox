#!/usr/bin/env python3
"""
Naming normalizer that normalizes file and folder names to a standard format.

Converts file and directory names to lowercase with underscores, removing special
characters. Supports ignore patterns (gitignore-style) to skip specific files
and directories. Handles case-insensitive filesystems correctly and detects
naming conflicts.
"""

import argparse
import fnmatch
import os
import re
import sys
import unicodedata
from pathlib import Path


def load_ignore_patterns(ignore_file=".ignore"):
    """
    Load ignore patterns from .ignore file (gitignore-style).

    Args:
        ignore_file: Path to ignore file

    Returns:
        List of ignore patterns
    """
    ignore_path = Path(ignore_file)
    patterns = []

    if ignore_path.exists():
        try:
            with open(ignore_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith("#"):
                        continue
                    patterns.append(line)
        except Exception as e:
            print(f"Warning: Could not read .ignore: {e}.", file=sys.stderr)

    return patterns


def _normalize_pattern(pattern):
    """Normalize a gitignore pattern by handling special prefixes/suffixes."""
    negated = pattern.startswith("!")
    if negated:
        pattern = pattern[1:].strip()

    root_relative = pattern.startswith("/")
    if root_relative:
        pattern = pattern[1:]

    dir_only = pattern.endswith("/")
    if dir_only:
        pattern = pattern[:-1]

    return pattern, negated, root_relative, dir_only


def _check_pattern_match(pattern, path_str, path_parts, root_relative):
    """Check if a pattern matches a path."""
    # Handle special gitignore pattern: .* means "starts with dot"
    if pattern == ".*":
        # Check if any part of the path starts with a dot
        if path_parts:
            return any(part.startswith(".") for part in path_parts)
        # If path_parts is empty, check the path string directly
        # Also check for dot-prefixed files in subdirectories
        return path_str.startswith(".") or "/." in path_str

    # Convert ** to wildcard matching for recursive patterns
    fnmatch_pattern = pattern.replace("**/", "*").replace("/**", "*").replace("**", "*")

    if root_relative:
        # Match from root
        return (fnmatch.fnmatch(path_str, fnmatch_pattern) or
                fnmatch.fnmatch(path_str, fnmatch_pattern + "/*"))

    # Match anywhere in path
    if (fnmatch.fnmatch(path_str, "*" + fnmatch_pattern) or
            fnmatch.fnmatch(path_str, "*" + fnmatch_pattern + "/*")):
        return True

    # Check path parts
    for i in range(len(path_parts)):
        part = path_parts[i]
        subpath = "/".join(path_parts[i:])
        if (fnmatch.fnmatch(part, fnmatch_pattern) or
                fnmatch.fnmatch(subpath, fnmatch_pattern) or
                fnmatch.fnmatch(subpath, "*" + fnmatch_pattern) or
                fnmatch.fnmatch(subpath, fnmatch_pattern + "/*")):
            return True

    return False


def matches_ignore_pattern(path, patterns, root_path):
    """
    Check if a path matches any ignore pattern (gitignore-style).

    Args:
        path: Path to check (Path object)
        patterns: List of ignore patterns
        root_path: Root directory being checked (Path object)

    Returns:
        True if path should be ignored, False otherwise
    """
    if not patterns:
        return False

    # Get relative path from root
    try:
        rel_path = path.relative_to(root_path)
    except ValueError:
        return False

    # Convert to forward slashes for pattern matching (works on all platforms)
    path_str = str(rel_path).replace("\\", "/")
    path_parts = path_str.split("/") if path_str else []
    is_dir = path.is_dir()

    matched = False

    for pattern in patterns:
        # Normalize pattern
        pattern, negated, root_relative, dir_only = _normalize_pattern(pattern)

        # Skip empty patterns
        if not pattern:
            continue

        # Skip directory-only patterns for files
        if dir_only and not is_dir:
            continue

        # Check if pattern matches
        pattern_matches = _check_pattern_match(pattern, path_str, path_parts, root_relative)

        if pattern_matches:
            matched = not negated  # Negation un-ignores the path

    return matched


def _contains_non_latin_script(text):
    """
    Check if text contains characters from non-Latin scripts that should be preserved.

    This includes: Chinese, Japanese, Korean, Russian (Cyrillic), Hebrew, Arabic,
    Thai, Hindi, and other non-Latin scripts. Accented Latin characters (like é, ñ)
    are allowed to be normalized.

    Args:
        text: Text to check

    Returns:
        True if text contains non-Latin script characters, False otherwise
    """
    for char in text:
        code_point = ord(char)
        # Skip combining marks (accents, diacritics) - these can be normalized
        if unicodedata.category(char).startswith('M'):
            continue

        # CJK (Chinese, Japanese, Korean)
        if (0x4E00 <= code_point <= 0x9FFF or  # CJK Unified Ideographs
            0x3400 <= code_point <= 0x4DBF or  # CJK Extension A
            0x20000 <= code_point <= 0x2A6DF or  # CJK Extension B
            0x3040 <= code_point <= 0x309F or  # Hiragana
            0x30A0 <= code_point <= 0x30FF or  # Katakana
                0xAC00 <= code_point <= 0xD7AF):  # Hangul
            return True
        # Cyrillic (Russian, Bulgarian, etc.)
        if 0x0400 <= code_point <= 0x04FF:
            return True
        # Hebrew
        if 0x0590 <= code_point <= 0x05FF:
            return True
        # Arabic
        if (0x0600 <= code_point <= 0x06FF or
            0x0700 <= code_point <= 0x074F or
                0x0750 <= code_point <= 0x077F):
            return True
        # Thai
        if 0x0E00 <= code_point <= 0x0E7F:
            return True
        # Devanagari (Hindi, Sanskrit, etc.)
        if 0x0900 <= code_point <= 0x097F:
            return True
        # Greek (preserve Greek script)
        if 0x0370 <= code_point <= 0x03FF:
            return True
        # Armenian
        if 0x0530 <= code_point <= 0x058F:
            return True
        # Georgian
        if 0x10A0 <= code_point <= 0x10FF:
            return True
    return False


def normalize_name(name, keep_extension=True):
    """
    Normalize a name to lowercase with underscores, removing special characters.

    Preserves names containing non-Latin scripts (Chinese, Japanese, Korean, Russian,
    Hebrew, Arabic, etc.) to avoid corrupting international file names. Accented
    Latin characters (like é, ñ) are normalized to their ASCII equivalents.

    Args:
        name: Name to normalize
        keep_extension: If True, preserve file extension

    Returns:
        Normalized name (or original if it contains non-Latin scripts)
    """
    if keep_extension and "." in name:
        # Split into base name and extension
        parts = name.rsplit(".", 1)
        base_name = parts[0]
        extension = "." + parts[1]
    else:
        base_name = name
        extension = ""

    # Check if base name contains non-Latin scripts - if so, preserve as-is
    if _contains_non_latin_script(base_name):
        return name

    # Normalize unicode characters (e.g., é -> e)
    # This safely converts accented Latin characters to ASCII
    base_name = unicodedata.normalize("NFKD", base_name)
    base_name = base_name.encode("ascii", "ignore").decode("ascii")

    # Replace dashes with underscores
    base_name = base_name.replace("-", "_")

    # Replace spaces and special characters with underscores
    base_name = re.sub(r"[^\w]", "_", base_name)

    # Remove leading/trailing underscores
    base_name = base_name.strip("_")

    # Convert to lowercase
    base_name = base_name.lower()

    # If empty after normalization, use a default name
    if not base_name:
        base_name = "unnamed"

    return base_name + extension


def normalize_names(root_path, nested=False, dry_run=True, confirm=False, ignore_patterns=None):
    """
    Normalize all file and folder names in root_path.

    Args:
        root_path: Root directory to normalize
        nested: If True, process subdirectories recursively
        dry_run: If True, only show what would be renamed without actually renaming
        confirm: If True and dry_run is False, actually perform the renames
        ignore_patterns: List of ignore patterns (gitignore-style)
    """
    root_path = Path(root_path).resolve()
    rename_operations = []
    processed_count = 0
    print("Scanning files and directories...")

    def update_progress():
        """Update progress display every 1000 items."""
        if processed_count % 1000 == 0:
            print(f"Processed {processed_count} items... (found {len(rename_operations)} to rename)", flush=True)

    # Collect all paths that need to be renamed
    # We need to process directories first (top-down) to avoid path conflicts
    dirs_to_process = []
    files_to_process = []

    if nested:
        # Walk through all directories and files
        for root, dirs, files in os.walk(root_path):
            # Filter out ignored directories (modify dirs in-place to skip them in os.walk)
            dirs[:] = [d for d in dirs if not matches_ignore_pattern(Path(root) / d, ignore_patterns or [], root_path)]

            # Collect directory names
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                normalized_name = normalize_name(dir_name, keep_extension=False)
                if dir_name != normalized_name:
                    dirs_to_process.append((dir_path, normalized_name))
                processed_count += 1
                update_progress()

            # Collect file names
            for file_name in files:
                file_path = Path(root) / file_name
                # Skip if matches ignore pattern
                if matches_ignore_pattern(file_path, ignore_patterns or [], root_path):
                    processed_count += 1
                    update_progress()
                    continue
                normalized_name = normalize_name(file_name, keep_extension=True)
                if file_name != normalized_name:
                    files_to_process.append((file_path, normalized_name))
                processed_count += 1
                update_progress()
    else:
        # Only process root level
        try:
            items = list(root_path.iterdir())
            for item in items:
                # Skip if matches ignore pattern
                if matches_ignore_pattern(item, ignore_patterns or [], root_path):
                    processed_count += 1
                    update_progress()
                    continue
                if item.is_dir():
                    normalized_name = normalize_name(item.name, keep_extension=False)
                    if item.name != normalized_name:
                        dirs_to_process.append((item, normalized_name))
                else:
                    normalized_name = normalize_name(item.name, keep_extension=True)
                    if item.name != normalized_name:
                        files_to_process.append((item, normalized_name))
                processed_count += 1
                update_progress()
        except PermissionError:
            print(f"Warning: Permission denied accessing {root_path}", file=sys.stderr)

    # Always print final progress
    print(f"Processed {processed_count} items... (found {len(dirs_to_process) + len(files_to_process)} to rename)")

    # Process directories first (top-down order)
    dirs_to_process.sort(key=lambda x: len(x[0].parts), reverse=True)

    # Track normalized names per directory to detect conflicts
    # Key: parent directory path, Value: tuple of (existing_files_dict, assigned_names_set)
    # existing_files_dict: name -> Path (for case-sensitive checking on Mac)
    # assigned_names_set: set of names already assigned in this batch
    normalized_names_by_dir = {}

    # Process all rename operations
    for old_path, new_name in dirs_to_process + files_to_process:
        new_path = old_path.parent / new_name
        parent_dir = old_path.parent

        # Initialize tracking for this directory if needed
        if parent_dir not in normalized_names_by_dir:
            existing_files = {}
            # Store existing names in the directory as a dict: name -> actual Path
            # This helps with case-insensitive filesystem detection on Mac
            try:
                for item in parent_dir.iterdir():
                    existing_files[item.name] = item
            except (PermissionError, OSError):
                pass
            normalized_names_by_dir[parent_dir] = (existing_files, set())

        existing_files, assigned_names = normalized_names_by_dir[parent_dir]

        # Check if target already exists in filesystem (and it's not the same file)
        # This handles the case where a file with the normalized name already exists.
        # On Mac (case-insensitive filesystem), we check actual file names case-sensitively
        # to avoid false positives when only the case differs.
        existing_item = existing_files.get(new_name)
        if existing_item is not None and existing_item != old_path:
            print(f"Warning: Target already exists, skipping: {old_path} -> {new_path}", file=sys.stderr)
            continue

        # Check if this normalized name is already assigned to another item in this batch.
        # This handles the case where multiple items normalize to the same name.
        if new_name in assigned_names:
            print(f"Warning: Target already exists, skipping: {old_path} -> {new_path}", file=sys.stderr)
            continue

        # Mark this normalized name as used in this batch
        assigned_names.add(new_name)
        rename_operations.append((old_path, new_path))

    if not rename_operations:
        print("All names are already normalized!")
        return 0

    # Show what would be renamed
    print(f"\n{'DRY RUN - ' if dry_run else ''}Found {len(rename_operations)} item(s) to rename:")
    for old_path, new_path in rename_operations:
        print(f"  {old_path} -> {new_path}")

    # Only actually rename if both --no-dry-run and --confirm are True
    if dry_run:
        print("\nDry run mode: No changes were made. Use --no-dry-run --confirm to apply changes.")
        return len(rename_operations)
    elif confirm:
        # Actually perform the renames
        print("\nApplying renames...")
        success_count = 0
        error_count = 0

        for old_path, new_path in rename_operations:
            try:
                old_path.rename(new_path)
                success_count += 1
            except Exception as e:
                print(f"Error renaming {old_path} -> {new_path}: {e}", file=sys.stderr)
                error_count += 1

        print(f"\nRenamed {success_count} item(s) successfully.")
        if error_count > 0:
            print(f"Failed to rename {error_count} item(s).", file=sys.stderr)
        return success_count
    else:
        print("\nNo changes were made. Use --confirm to actually perform the renames.")
        return len(rename_operations)


def _should_use_gui():
    """Check if GUI mode should be enabled."""
    return "--gui" in sys.argv and "--ignore-gooey" not in sys.argv


def main():
    """Main function to parse arguments and run the naming normalizer."""
    use_gui = _should_use_gui()

    parser = argparse.ArgumentParser(
        description="Normalize file and folder names to a standard format"
    )
    parser.add_argument(
        "path",
        help="Root directory path to normalize"
    )
    parser.add_argument(
        "-n", "--nested",
        action="store_true",
        help="Process subdirectories recursively (default: False)"
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Disable dry run mode (default: dry run mode)"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirm and actually perform the renames (requires --no-dry-run)"
    )
    parser.add_argument(
        "-i", "--ignore",
        default=".ignore",
        help="Ignore file for patterns (default: .ignore)"
    )

    # Only add --gui and --ignore-gooey when NOT in GUI mode (hide them from Gooey UI)
    if not use_gui:
        parser.add_argument(
            "--gui",
            action="store_true",
            help="Enable GUI mode (default: command-line mode)"
        )
        parser.add_argument(
            "--ignore-gooey",
            action="store_true",
            help=argparse.SUPPRESS
        )

    args = parser.parse_args()

    # Validate path exists
    if not os.path.exists(args.path):
        print(f"Error: Path \"{args.path}\" does not exist.", file=sys.stderr)
        sys.exit(1)

    if not os.path.isdir(args.path):
        print(f"Error: \"{args.path}\" is not a directory.", file=sys.stderr)
        sys.exit(1)

    # Load ignore patterns
    # Try to find .ignore file: check specified path, script directory, then root_path
    root_path_obj = Path(args.path).resolve()
    script_dir = Path(__file__).parent.resolve()
    ignore_file_path = Path(args.ignore)

    # If not absolute and doesn't exist, try multiple locations
    if not ignore_file_path.is_absolute() and not ignore_file_path.exists():
        # Try in script directory first (where .ignore is bundled with the tool)
        try_ignore_path = script_dir / args.ignore
        if try_ignore_path.exists():
            ignore_file_path = try_ignore_path
        else:
            # Try in root_path (target directory)
            try_ignore_path = root_path_obj / args.ignore
            if try_ignore_path.exists():
                ignore_file_path = try_ignore_path

    ignore_patterns = load_ignore_patterns(ignore_file_path)
    if ignore_patterns:
        print(f"Loaded {len(ignore_patterns)} ignore pattern(s) from {ignore_file_path}")

    # Run the normalization
    dry_run = not args.no_dry_run
    normalize_names(args.path, nested=args.nested, dry_run=dry_run, confirm=args.confirm, ignore_patterns=ignore_patterns)


if __name__ == "__main__":
    if _should_use_gui():
        from gooey import Gooey
        main = Gooey(program_name="Naming Normalizer", default_size=(500, 600), optional_cols=1)(main)

    main()
