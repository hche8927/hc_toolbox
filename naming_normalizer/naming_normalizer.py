#!/usr/bin/env python3
"""
Minimalistic naming normalizer that normalizes file and folder names to a standard format.
"""

import argparse
import os
import re
import sys
import unicodedata
from pathlib import Path


def normalize_name(name, keep_extension=True):
    """
    Normalize a name to lowercase with underscores, removing special characters.

    Args:
        name: Name to normalize
        keep_extension: If True, preserve file extension

    Returns:
        Normalized name
    """
    if keep_extension and "." in name:
        # Split into base name and extension
        parts = name.rsplit(".", 1)
        base_name = parts[0]
        extension = "." + parts[1]
    else:
        base_name = name
        extension = ""

    # Normalize unicode characters (e.g., é -> e)
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


def normalize_names(root_path, nested=False, dry_run=True, confirm=False):
    """
    Normalize all file and folder names in root_path.

    Args:
        root_path: Root directory to normalize
        nested: If True, process subdirectories recursively
        dry_run: If True, only show what would be renamed without actually renaming
        confirm: If True and dry_run is False, actually perform the renames
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

    # Track normalized names per directory to detect conflicts within the batch
    # Key: parent directory path, Value: set of normalized names already assigned
    normalized_names_by_dir = {}

    # Process all rename operations
    for old_path, new_name in dirs_to_process + files_to_process:
        new_path = old_path.parent / new_name
        parent_dir = old_path.parent

        # Initialize tracking for this directory if needed
        if parent_dir not in normalized_names_by_dir:
            normalized_names_by_dir[parent_dir] = set()
            # Add existing names in the directory to the set (to detect conflicts with existing files)
            try:
                for item in parent_dir.iterdir():
                    normalized_names_by_dir[parent_dir].add(item.name)
            except (PermissionError, OSError):
                pass

        # Check if target already exists in filesystem (and it's not the same file)
        # This handles the case where a file with the normalized name already exists
        if new_path.exists() and new_path != old_path:
            print(f"Warning: Target already exists, skipping: {old_path} -> {new_path}", file=sys.stderr)
            continue

        # Check if this normalized name is already assigned to another item in this batch
        # This handles the case where multiple items normalize to the same name
        if new_name in normalized_names_by_dir[parent_dir]:
            # Only skip if it's not the same file (i.e., the file is already normalized)
            if new_path != old_path:
                print(f"Warning: Target already exists, skipping: {old_path} -> {new_path}", file=sys.stderr)
                continue

        # Mark this normalized name as used (even if it's the same file, to track it)
        normalized_names_by_dir[parent_dir].add(new_name)
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

    # Run the normalization
    dry_run = not args.no_dry_run
    normalize_names(args.path, nested=args.nested, dry_run=dry_run, confirm=args.confirm)


if __name__ == "__main__":
    if _should_use_gui():
        from gooey import Gooey
        main = Gooey(program_name="Naming Normalizer", default_size=(500, 600), optional_cols=1)(main)

    main()
