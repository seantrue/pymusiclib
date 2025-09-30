#!/usr/bin/env python3
"""
Servify - Music Library Organization Tool
==========================================

A tool for organizing music files into a Plex-compatible directory structure
based on metadata from a CSV file exported from MusicLib.

Features:
- Organizes files into Artist/Album/Track structure
- Supports dry-run mode for testing
- Configurable output directory
- Progress reporting and error handling
- Flexible track naming patterns
"""

import argparse
import contextlib
import io
import os
import shutil
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd


class MusicConductor:
    """Music file organization conductor."""

    def __init__(
        self,
        csv_file: str,
        output_dir: str = "plex",
        dry_run: bool = False,
        verbose: bool = False,
        skip_existing: bool = True,
        track_format: str = "{track:02d} - {title}",
    ):
        """Initialize the conductor.

        Args:
            csv_file: Path to CSV file with music metadata
            output_dir: Output directory for organized files
            dry_run: If True, show what would be done without making changes
            verbose: Enable verbose output
            skip_existing: Skip files that already exist in destination
            track_format: Format string for track filenames
        """
        self.csv_file = csv_file
        self.output_dir = Path(output_dir)
        self.dry_run = dry_run
        self.verbose = verbose
        self.skip_existing = skip_existing
        self.track_format = track_format

        # Statistics
        self.stats = {
            "processed": 0,
            "skipped": 0,
            "copied": 0,
            "errors": 0,
        }

    def load_music_data(self) -> pd.DataFrame:
        """Load and validate music data from CSV."""
        try:
            df = pd.read_csv(self.csv_file).fillna("")
            print(f"📥 Loaded {len(df)} tracks from {self.csv_file}")
            return df
        except FileNotFoundError:
            print(f"❌ Error: CSV file not found: {self.csv_file}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            sys.exit(1)

    def sanitize_filename(self, name: str) -> str:
        """Sanitize filename by removing/replacing problematic characters."""
        # Replace problematic characters
        replacements = {
            "/": "-",
            "\\": "-",
            ":": " -",
            "*": "",
            "?": "",
            '"': "'",
            "<": "(",
            ">": ")",
            "|": "-",
        }

        for old, new in replacements.items():
            name = name.replace(old, new)

        # Remove multiple spaces and strip
        name = " ".join(name.split())
        return name.strip()

    def get_destination_path(self, song: pd.Series) -> Optional[Path]:
        """Generate destination path for a song."""
        # Use album_artist if available, otherwise fall back to artist
        artist = song.album_artist if song.album_artist else song.artist
        if not artist:
            print(f"⚠️  Skipping: No artist for '{song.title}'")
            return None

        album = song.album
        if not album:
            print(f"⚠️  Skipping: No album for '{song.title}' by {artist}")
            return None

        title = song.title
        if not title:
            print(f"⚠️  Skipping: No title for track by {artist}")
            return None

        # Sanitize all components
        artist = self.sanitize_filename(artist)
        album = self.sanitize_filename(album)
        title = self.sanitize_filename(title)

        # Format track number
        track_num = int(song.track_number) if song.track_number else 0

        # Format filename using the template
        filename = self.track_format.format(
            track=track_num,
            title=title,
            artist=song.artist,
            album=album,
        )

        # Add file extension
        ext = song.file_extension
        if ext and not ext.startswith('.'):
            ext = f".{ext}"

        return self.output_dir / artist / album / f"{filename}{ext}"

    def validate_source_file(self, song: pd.Series) -> bool:
        """Validate that source file exists and has correct extension."""
        if not song.file_path:
            if self.verbose:
                print(f"⚠️  No file path for '{song.title}'")
            return False

        if not song.track_number:
            if self.verbose:
                print(f"⚠️  No track number for '{song.title}'")
            return False

        source_path = Path(song.file_path)
        if not source_path.exists():
            print(f"❌ Source file not found: {song.file_path}")
            return False

        # Check file extension consistency
        ext = song.file_extension
        if ext and not song.file_path.endswith(ext):
            print(f"⚠️  Extension mismatch: expected {ext}, got {source_path.suffix}")
            return False

        return True

    def copy_file(self, source: Path, destination: Path, song: pd.Series) -> bool:
        """Copy a file from source to destination."""
        try:
            # Create destination directory
            destination.parent.mkdir(parents=True, exist_ok=True)

            if self.dry_run:
                print(f"🔍 Would copy: {source} → {destination}")
                return True
            else:
                shutil.copy2(source, destination)
                if self.verbose:
                    print(f"✅ Copied: {song.artist} - {song.title}")
                return True

        except Exception as e:
            print(f"❌ Error copying {source}: {e}")
            return False

    def process_song(self, song: pd.Series) -> bool:
        """Process a single song."""
        self.stats["processed"] += 1

        # Validate source file
        if not self.validate_source_file(song):
            self.stats["skipped"] += 1
            return False

        # Get destination path
        dest_path = self.get_destination_path(song)
        if not dest_path:
            self.stats["skipped"] += 1
            return False

        # Check if destination already exists
        if dest_path.exists() and self.skip_existing:
            if self.verbose:
                print(f"⏭️  Exists: {song.artist} - {song.title}")
            self.stats["skipped"] += 1
            return False

        # Copy the file
        source_path = Path(song.file_path)
        if self.copy_file(source_path, dest_path, song):
            self.stats["copied"] += 1
            return True
        else:
            self.stats["errors"] += 1
            return False

    def organize_music(self) -> None:
        """Main method to organize music files."""
        print("🎵 Music Library Conductor")
        print("=" * 50)

        if self.dry_run:
            print("🔍 DRY RUN MODE - No files will be copied")

        print(f"📂 Output directory: {self.output_dir}")
        print(f"📝 Track format: {self.track_format}")
        print()

        # Load music data
        df = self.load_music_data()

        # Process each song
        for index, song in df.iterrows():
            self.process_song(song)

        # Print final statistics
        self.print_statistics()

    def print_statistics(self) -> None:
        """Print final processing statistics."""
        print("\n📊 Processing Summary:")
        print("=" * 30)
        print(f"  Tracks processed: {self.stats['processed']:,}")
        print(f"  Files copied: {self.stats['copied']:,}")
        print(f"  Files skipped: {self.stats['skipped']:,}")
        print(f"  Errors: {self.stats['errors']:,}")

        if self.stats["errors"] > 0:
            print(f"\n⚠️  {self.stats['errors']} errors occurred during processing")
        elif self.stats["copied"] > 0:
            print(f"\n✅ Successfully organized {self.stats['copied']} music files!")
        else:
            print(f"\n ℹ️ No files were copied (all were skipped or errors occurred)")


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Organize music files into Plex-compatible directory structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with default settings
  python utils/servify.py library.csv

  # Dry run to see what would be organized
  python utils/servify.py library.csv --dry-run

  # Custom output directory and verbose output
  python utils/servify.py library.csv --output /media/music --verbose

  # Custom track naming format
  python utils/servify.py library.csv --track-format "{track:03d}. {title}"

  # Force overwrite existing files
  python utils/servify.py library.csv --force

  # Include disc number in track format (if available in CSV)
  python utils/servify.py library.csv --track-format "CD{disc:01d}-{track:02d} - {title}"

Directory Structure:
  Servify organizes files as: Artist/Album/Track - Title.ext
  Example: Led Zeppelin/IV/04 - Stairway to Heaven.mp3
        """,
    )

    # Required arguments
    parser.add_argument(
        "csv_file",
        help="CSV file containing music metadata (exported from MusicLib)"
    )

    # Output options
    parser.add_argument(
        "--output", "-o",
        default="plex",
        help="Output directory for organized music files (default: plex)"
    )

    parser.add_argument(
        "--track-format", "-f",
        default="{track:02d} - {title}",
        help="Format string for track filenames (default: '{track:02d} - {title}')"
    )

    # Behavior options
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be done without making any changes"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files instead of skipping them"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress all output except errors"
    )

    return parser


def main():
    """Main function for command-line usage."""
    parser = create_parser()
    args = parser.parse_args()

    # Validate CSV file exists
    if not os.path.exists(args.csv_file):
        print(f"❌ Error: CSV file not found: {args.csv_file}")
        sys.exit(1)

    # Suppress output in quiet mode
    if args.quiet:
        # Redirect stdout to nowhere for quiet mode
        stdout_backup = sys.stdout

        @contextlib.contextmanager
        def quiet_output():
            try:
                sys.stdout = io.StringIO()
                # Keep stderr for errors
                yield
            finally:
                sys.stdout = stdout_backup

        context = quiet_output()
    else:
        @contextlib.contextmanager
        def no_quiet():
            yield
        context = no_quiet()

    # Create and run conductor
    with context:
        conductor = MusicConductor(
            csv_file=args.csv_file,
            output_dir=args.output,
            dry_run=args.dry_run,
            verbose=args.verbose,
            skip_existing=not args.force,
            track_format=args.track_format,
        )

        try:
            conductor.organize_music()
        except KeyboardInterrupt:
            print("\n\n⏹️  Operation cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)

    # Show final summary in quiet mode
    if args.quiet:
        print(f"Processed: {conductor.stats['copied']} copied, {conductor.stats['skipped']} skipped, {conductor.stats['errors']} errors")


if __name__ == "__main__":
    main()