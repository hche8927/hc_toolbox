#!/usr/bin/env python3
"""
Minimalistic video frame extractor that extracts frames from video files.
"""

import argparse
import os
import sys
import time
from pathlib import Path

import cv2


class VideoFrameExtractor:
    """Extract frames from video files with various options."""

    # Interpolation method mapping
    INTERPOLATION_METHODS = {
        'nearest': cv2.INTER_NEAREST,
        'linear': cv2.INTER_LINEAR,
        'cubic': cv2.INTER_CUBIC,
        'area': cv2.INTER_AREA,
        'lanczos4': cv2.INTER_LANCZOS4,
    }

    def __init__(self, video_path, output_dir="frames", frame_interval=1,
                 scale=1.0, interpolation='linear'):
        """
        Initialize the video frame extractor.

        Args:
            video_path (str): Path to the input video file
            output_dir (str): Directory to save extracted frames
            frame_interval (int): Extract every Nth frame (1 = every frame)
            scale (float): Scale factor (e.g., 2.0 for 2x, 0.5 for half, 1.0 = original size)
            interpolation (str): Interpolation method ('nearest', 'linear', 'cubic', 'area', 'lanczos4')
        """
        self.video_path = Path(video_path)
        self.output_dir = Path(output_dir)
        self.frame_interval = frame_interval
        self.format = "png"  # Always PNG
        self.scale = scale
        self.interpolation = self._get_interpolation(interpolation)

        # Validate inputs
        self._validate_inputs()

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_interpolation(self, interpolation):
        """Get interpolation method constant from string."""
        interpolation_lower = interpolation.lower()
        if interpolation_lower not in self.INTERPOLATION_METHODS:
            raise ValueError(
                f"Interpolation must be one of: {', '.join(self.INTERPOLATION_METHODS.keys())}"
            )
        return self.INTERPOLATION_METHODS[interpolation_lower]

    def _get_interpolation_name(self):
        """Get interpolation method name from constant."""
        for name, method in self.INTERPOLATION_METHODS.items():
            if method == self.interpolation:
                return name
        return 'unknown'

    def _validate_inputs(self):
        """Validate input parameters."""
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {self.video_path}")

        if self.frame_interval < 1:
            raise ValueError("Frame interval must be at least 1")

        if self.scale <= 0:
            raise ValueError("Scale factor must be greater than 0")

    def get_video_info(self):
        """Get video information."""
        cap = cv2.VideoCapture(str(self.video_path))

        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {self.video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0

        cap.release()

        return {
            'fps': fps,
            'frame_count': frame_count,
            'width': width,
            'height': height,
            'duration': duration
        }

    def extract_frames(self, start_frame=0, end_frame=-1):
        """
        Extract frames from the video.

        Args:
            start_frame (int): Start frame number (0 = beginning)
            end_frame (int): End frame number (-1 = last frame)

        Returns:
            int: Number of frames extracted
        """
        cap = cv2.VideoCapture(str(self.video_path))

        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {self.video_path}")

        # Get video info
        video_info = self.get_video_info()
        total_frames = video_info['frame_count']

        # Handle end_frame: -1 means last frame
        if end_frame == -1:
            end_frame = total_frames
        elif end_frame > total_frames:
            end_frame = total_frames

        # Validate start_frame
        if start_frame < 0:
            start_frame = 0
        if start_frame >= total_frames:
            raise ValueError(
                f"Start frame {start_frame} is beyond video length ({total_frames} frames)"
            )

        # Set starting position
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        frame_number = start_frame
        extracted_count = 0

        print(f"Extracting frames from {self.video_path.name}")
        print(f"Video info: {video_info['width']}x{video_info['height']}, "
              f"{video_info['fps']:.2f} FPS, {video_info['duration']:.2f}s")
        if self.scale != 1.0:
            # Calculate output dimensions
            target_width = int(video_info['width'] * self.scale)
            target_height = int(video_info['height'] * self.scale)
            print(
                f"Resize: {target_width}x{target_height} "
                f"(scale: {self.scale}x, interpolation: {self._get_interpolation_name()})"
            )
        print(f"Frame range: {start_frame} to {end_frame} (interval: {self.frame_interval})")
        print(f"Output directory: {self.output_dir}")
        print("-" * 50)

        start_time_extract = time.time()

        while frame_number < end_frame:
            ret, frame = cap.read()

            if not ret:
                break

            # Extract frame if it matches the interval
            if (frame_number - start_frame) % self.frame_interval == 0:
                # Resize frame if needed
                if self.scale != 1.0:
                    frame = self._resize_frame(frame, video_info['width'], video_info['height'])

                # Generate filename (always PNG)
                filename = f"{frame_number:06d}.png"
                output_path = self.output_dir / filename

                # Save frame as PNG
                cv2.imwrite(str(output_path), frame)

                extracted_count += 1

                # Simple progress indicator
                if extracted_count % 10 == 0:
                    frame_range = end_frame - start_frame
                    progress = (frame_number - start_frame) / frame_range if frame_range > 0 else 1.0
                    print(f"Progress: {progress:.1%} ({extracted_count} frames extracted)")

            frame_number += 1

        cap.release()

        # Always print 100% at the end
        if extracted_count > 0:
            print(f"Progress: 100.0% ({extracted_count} frames extracted)")

        end_time_extract = time.time()
        duration = end_time_extract - start_time_extract

        print("-" * 50)
        print(f"Extraction completed!")
        print(f"Total frames extracted: {extracted_count}")
        if duration > 0:
            print(f"Time taken: {duration:.2f} seconds")
            print(f"Average speed: {extracted_count/duration:.1f} frames/second")

        return extracted_count

    def _resize_frame(self, frame, original_width, original_height):
        """
        Resize frame using scale factor.

        Args:
            frame: Frame to resize
            original_width: Original frame width
            original_height: Original frame height

        Returns:
            Resized frame
        """
        if self.scale == 1.0:
            return frame

        # Calculate target dimensions using scale factor
        target_width = int(original_width * self.scale)
        target_height = int(original_height * self.scale)

        # Resize frame
        resized = cv2.resize(frame, (target_width, target_height), interpolation=self.interpolation)
        return resized


def _get_default_output_dir():
    """Get default output directory (Downloads/frames)."""
    downloads_dir = Path.home() / "Downloads"
    return downloads_dir / "frames"


def _should_use_gui():
    """Check if GUI mode should be enabled."""
    return "--gui" in sys.argv and "--ignore-gooey" not in sys.argv


def main():
    """Main function to parse arguments and run the frame extractor."""
    use_gui = _should_use_gui()

    parser = argparse.ArgumentParser(
        description="Extract frames from video files"
    )
    parser.add_argument(
        "video",
        help="Path to input video file"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show video information and exit"
    )
    default_output = str(_get_default_output_dir())
    parser.add_argument(
        "-o", "--output",
        default=default_output,
        help=f"Output directory for frames (default: {default_output})"
    )
    parser.add_argument(
        "-i", "--interval",
        type=int,
        default=1,
        help="Extract every Nth frame (default: 1)"
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=1.0,
        help="Scale factor (e.g., 2.0 for 2x, 0.5 for half size, default: 1.0)"
    )
    parser.add_argument(
        "--interpolation",
        choices=['nearest', 'linear', 'cubic', 'area', 'lanczos4'],
        default='linear',
        help="Interpolation method for resizing (default: linear)"
    )
    parser.add_argument(
        "-s", "--start",
        type=int,
        default=0,
        help="Start frame number (default: 0)"
    )
    parser.add_argument(
        "-e", "--end",
        type=int,
        default=-1,
        help="End frame number (-1 for last frame, default: -1)"
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

    # Validate video file exists
    if not os.path.exists(args.video):
        print(f"Error: Video file \"{args.video}\" does not exist.", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(args.video):
        print(f"Error: \"{args.video}\" is not a file.", file=sys.stderr)
        sys.exit(1)

    # Use output directory as-is (default is already absolute path to Downloads/frames)
    output_dir = Path(args.output)

    # Show video info if requested
    if args.info:
        extractor = VideoFrameExtractor(
            video_path=args.video,
            output_dir=output_dir,
            frame_interval=args.interval,
            scale=args.scale,
            interpolation=args.interpolation
        )
        info = extractor.get_video_info()
        print(f"\nVideo: {args.video}")
        print(f"Resolution: {info['width']}x{info['height']}")
        print(f"FPS: {info['fps']:.2f}")
        print(f"Duration: {info['duration']:.2f} seconds")
        print(f"Total frames: {info['frame_count']}")
        return

    # Create extractor and extract frames
    extractor = VideoFrameExtractor(
        video_path=args.video,
        output_dir=output_dir,
        frame_interval=args.interval,
        scale=args.scale,
        interpolation=args.interpolation
    )

    extractor.extract_frames(
        start_frame=args.start,
        end_frame=args.end
    )


if __name__ == "__main__":
    if _should_use_gui():
        from gooey import Gooey
        main = Gooey(program_name="Video Frame Extractor", default_size=(600, 950), optional_cols=1)(main)

    main()
