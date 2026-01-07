#!/usr/bin/env python3
"""
Minimalistic naming checker that validates file and folder names against a regex pattern.
"""

import argparse
import fnmatch
import os
import re
import sys
from datetime import datetime
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


def _get_default_output_dir():
    """Get default output directory (Downloads)."""
    downloads_dir = Path.home() / "Downloads"
    return downloads_dir


def check_names(root_path, pattern, ignore_patterns, output_dir):
    """
    Check all file and folder names in root_path against the regex pattern.

    Args:
        root_path: Root directory to check
        pattern: Compiled regex pattern
        ignore_patterns: List of ignore patterns
        output_dir: Directory to save output file
    """
    invalid_paths = []
    root_path = Path(root_path).resolve()
    checked_count = 0
    print("Checking files and directories...")

    def update_progress():
        """Update progress display every 1000 items."""
        if checked_count % 1000 == 0:
            print(f"Checked {checked_count} items... (found {len(invalid_paths)} invalid)", flush=True)

    # Walk through all directories and files
    for root, dirs, files in os.walk(root_path):
        # Filter out ignored directories (modify dirs in-place to skip them)
        dirs[:] = [d for d in dirs if not matches_ignore_pattern(Path(root) / d, ignore_patterns, root_path)]

        # Check directory names
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            if not pattern.match(dir_name):
                invalid_paths.append(str(dir_path))
            checked_count += 1
            update_progress()

        # Check file names
        for file_name in files:
            file_path = Path(root) / file_name
            # Skip if matches ignore pattern
            if matches_ignore_pattern(file_path, ignore_patterns, root_path):
                checked_count += 1
                update_progress()
                continue
            # Check only the base name (without extension) for files
            base_name = file_name.rsplit(".", 1)[0] if "." in file_name else file_name
            if not pattern.match(base_name):
                invalid_paths.append(str(file_path))
            checked_count += 1
            update_progress()

    # Always print final progress
    print(f"Checked {checked_count} items... (found {len(invalid_paths)} invalid)")

    # Save results if there are invalid paths
    if invalid_paths:
        output_dir = Path(output_dir)
        # Ensure output directory exists (Downloads should exist, but just in case)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"invalid_paths_{timestamp}.txt"

        with open(output_file, "w", encoding="utf-8") as f:
            for path in invalid_paths:
                f.write(f"{path}\n")

        print(f"Results saved to: {output_file}")
        return len(invalid_paths)
    else:
        print("All paths are valid!")
        return 0


def _should_use_gui():
    """Check if GUI mode should be enabled."""
    return "--gui" in sys.argv and "--ignore-gooey" not in sys.argv


def main():
    """Main function to parse arguments and run the naming checker."""
    use_gui = _should_use_gui()

    parser = argparse.ArgumentParser(
        description="Check file and folder names against a regex pattern"
    )
    parser.add_argument(
        "path",
        help="Root directory path to check"
    )
    parser.add_argument(
        "-r", "--regex",
        default="^[a-z0-9_]+$",
        help="Regex pattern to validate names (default: ^[a-z0-9_]+$)"
    )
    parser.add_argument(
        "-i", "--ignore",
        default=".ignore",
        help="Ignore file for patterns (default: .ignore)"
    )
    default_output = str(_get_default_output_dir())
    parser.add_argument(
        "-o", "--output",
        default=default_output,
        help=f"Output directory for results (default: {default_output})"
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

    # Get regex pattern from argument
    regex_pattern = args.regex
    print(f"Using regex pattern: {regex_pattern}")

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

    # Compile regex pattern
    try:
        pattern = re.compile(regex_pattern)
    except re.error as e:
        print(f"Error: Invalid regex pattern: {e}", file=sys.stderr)
        sys.exit(1)

    # Run the check
    check_names(args.path, pattern, ignore_patterns, args.output)


if __name__ == "__main__":
    if _should_use_gui():
        from gooey import Gooey
        main = Gooey(program_name="Naming Checker", default_size=(700, 600))(main)

    main()
