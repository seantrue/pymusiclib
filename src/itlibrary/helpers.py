#!/usr/bin/env python3
"""
ITLibrary Bridge Helper Utilities
Comprehensive utilities and demonstrations for the ITLibrary bridge
"""

import os
import sys
import time
from typing import Any, List, Optional

import numpy as np
import pandas as pd

# Import from the same package to avoid circular imports
try:
    from . import ITLibrary, ITLibraryError, MediaItem, Playlist
except ImportError:
    print("ITLibrary Bridge core not available. Please build and install first:")
    print("  make build && make install-dev")
    sys.exit(1)


class StopWatch:
    """Simple stopwatch utility for timing operations."""

    def __init__(self):
        self.elapsed_time = 0
        self.clicks = 0
        self._start = 0.0

    def __enter__(self):
        self._start = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed_time += time.time() - self._start
        self.clicks += 1

    def __str__(self):
        if self.clicks == 0:
            return "No clicks"
        return f"⏱ Elapsed {self.elapsed_time:.3f} sec for {self.clicks} steps, average = {self.elapsed_time / self.clicks:.3f}"


class LibraryBenchmark:
    """Benchmark and demonstration utilities for iTunes Library access."""

    def __init__(self):
        self.library: Optional[ITLibrary] = None

    def initialize_library(self) -> bool:
        """Initialize the iTunes Library connection."""
        if self.library is not None:
            return True  # Already initialized

        try:
            self.library = ITLibrary()
            return True
        except ITLibraryError as e:
            print(f"Failed to initialize library: {e}")
            return False

    def benchmark_library_access(self) -> None:
        """Benchmark basic library access operations."""
        print("iTunes Library Access Benchmark")
        print("=" * 50)

        if not self.initialize_library():
            return

        stopwatch = StopWatch()

        # Benchmark library info access
        with stopwatch:
            media_count = self.library.media_items_count
            playlists_count = self.library.playlists_count
            media_folder = self.library.media_folder_location
            music_folder = self.library.music_folder_location

        print(f"Library info access: {stopwatch}")
        print(f"  Media items: {media_count}")
        print(f"  Playlists: {playlists_count}")
        print(f"  Media folder: {media_folder}")
        print(f"  Music folder: {music_folder}")

        # Benchmark media item access
        stopwatch = StopWatch()
        sample_size = min(100, media_count)

        with stopwatch:
            for i in range(sample_size):
                item = self.library.get_media_item(i)

        print(f"Media item access ({sample_size} items): {stopwatch}")

        # Benchmark playlist access
        stopwatch = StopWatch()
        playlist_sample_size = min(20, playlists_count)

        with stopwatch:
            for i in range(playlist_sample_size):
                playlist = self.library.get_playlist(i)

        print(f"Playlist access ({playlist_sample_size} playlists): {stopwatch}")

    def show_library_summary(self) -> None:
        """Display a comprehensive summary of the iTunes Library."""
        print("iTunes Library Summary")
        print("=" * 40)

        if not self.initialize_library():
            return

        # Basic library info
        print(f"Media Items: {self.library.media_items_count:,}")
        print(f"Playlists: {self.library.playlists_count:,}")
        print(f"Media Folder: {self.library.media_folder_location}")
        print(f"Music Folder: {self.library.music_folder_location}")

        # Sample media items
        print("\nSample Media Items:")
        sample_size = min(10, self.library.media_items_count)
        for i in range(sample_size):
            item = self.library.get_media_item(i)
            duration_str = (
                f"{item.duration // 60}:{item.duration % 60:02d}"
                if item.duration > 0
                else "unknown"
            )
            print(f"  {i + 1:2d}. {item.title} - {item.artist} ({duration_str})")

        # Sample playlists
        print("\nSample Playlists:")
        playlist_sample_size = min(10, self.library.playlists_count)
        for i in range(playlist_sample_size):
            playlist = self.library.get_playlist(i)
            print(f"  {i + 1:2d}. {playlist.name} ({playlist.item_count} items)")

    def search_demonstration(self, search_terms: List[str]) -> None:
        """Demonstrate search functionality with given terms."""
        print("Search Demonstration")
        print("=" * 30)

        if not self.initialize_library():
            return

        for term in search_terms:
            print(f"\nSearching for: '{term}'")

            title_matches = self.library.search_by_title(term)
            print(f"  Title matches: {title_matches}")

            artist_matches = self.library.search_by_artist(term)
            print(f"  Artist matches: {artist_matches}")

    def analyze_library_statistics(self) -> None:
        """Analyze and display library statistics."""
        print("Library Statistics Analysis")
        print("=" * 40)

        if not self.initialize_library():
            return

        # Collect statistics
        total_items = self.library.media_items_count
        if total_items == 0:
            print("No media items found in library.")
            return

        # Sample analysis (first 1000 items for performance)
        sample_size = min(1000, total_items)
        durations = []
        years = []
        artists = set()
        albums = set()

        print(f"Analyzing {sample_size:,} items...")

        for i in range(sample_size):
            item = self.library.get_media_item(i)

            if item.duration > 0:
                durations.append(item.duration)

            if item.year > 0:
                years.append(item.year)

            if item.artist:
                artists.add(item.artist)

            if item.album:
                albums.add(item.album)

        # Display statistics
        if durations:
            avg_duration = sum(durations) / len(durations)
            total_duration = sum(durations)
            print(
                f"Average track duration: {avg_duration:.1f} seconds ({avg_duration / 60:.1f} minutes)"
            )
            print(
                f"Total sampled duration: {total_duration // 3600:.0f}h {(total_duration % 3600) // 60:.0f}m"
            )

        if years:
            print(f"Year range: {min(years)} - {max(years)}")

        print(f"Unique artists (in sample): {len(artists):,}")
        print(f"Unique albums (in sample): {len(albums):,}")

        # Extrapolate to full library
        if sample_size < total_items:
            artist_estimate = int(len(artists) * (total_items / sample_size))
            album_estimate = int(len(albums) * (total_items / sample_size))
            print(f"\nEstimated total unique artists: {artist_estimate:,}")
            print(f"Estimated total unique albums: {album_estimate:,}")

    def export_library_to_dataframe(
        self, audio_only: bool = True, limit: Optional[int] = None
    ) -> pd.DataFrame:
        """Export all iTunes Library media items to a pandas DataFrame.

        This function extracts comprehensive metadata for all tracks, optimized for
        migrating media to another server or media management system.

        Args:
            audio_only: If True, filter out video content (default: True)
            limit: Optional limit on number of items to export (useful for testing)

        Returns:
            pandas.DataFrame with comprehensive track metadata including file paths
        """
        print("Exporting iTunes Library to DataFrame...")

        if not self.initialize_library():
            raise ITLibraryError("Failed to initialize iTunes Library for export")

        total_items = self.library.media_items_count
        if total_items == 0:
            print("No media items found in library.")
            return pd.DataFrame()

        # Determine how many items to process
        items_to_process = min(limit, total_items) if limit else total_items
        print(f"Processing {items_to_process:,} of {total_items:,} items...")

        # Collect all metadata
        data = []
        processed = 0

        for i in range(items_to_process):
            try:
                item = self.library.get_media_item(i)

                # Filter out video content if requested
                if audio_only and item.is_video:
                    continue

                # Convert MediaItem to dictionary for DataFrame
                item_data = {
                    # Core identification
                    "index": item.index,
                    "title": item.title,
                    "artist": item.artist,
                    "album": item.album,
                    "album_artist": item.album_artist,
                    "genre": item.genre,
                    # Track information
                    "track_number": item.track_number,
                    "year": item.year,
                    "duration_seconds": item.duration,
                    "duration_ms": item.total_time_ms,
                    # Audio technical specs
                    "bitrate_kbps": item.bitrate,
                    "sample_rate_hz": item.sample_rate,
                    "file_size_bytes": item.file_size,
                    "format_kind": item.kind,
                    # Usage statistics
                    "play_count": item.play_count,
                    "rating": item.rating,
                    # File location (critical for migration)
                    "file_path": item.location,
                    "is_video": item.is_video,
                    # Date information
                    "date_added": item.date_added,
                }

                # Add derived fields useful for migration
                if item.file_size > 0:
                    item_data["file_size_mb"] = round(item.file_size / (1024 * 1024), 2)
                else:
                    item_data["file_size_mb"] = None

                # Determine if file is local or cloud/remote
                if item.location:
                    item_data["is_local_file"] = item.location.startswith("/")
                    item_data["file_extension"] = (
                        item.location.split(".")[-1].lower()
                        if "." in item.location
                        else None
                    )
                else:
                    item_data["is_local_file"] = False
                    item_data["file_extension"] = None

                # Create a unique identifier for deduplication
                item_data["unique_id"] = (
                    f"{item.artist or 'Unknown'}_{item.album or 'Unknown'}_{item.title or 'Unknown'}_{item.track_number}"
                )

                data.append(item_data)
                processed += 1

                # Progress indicator for large libraries
                if processed % 1000 == 0:
                    print(f"  Processed {processed:,} items...")

            except Exception as e:
                print(f"Warning: Error processing item {i}: {e}")
                continue

        print(f"Successfully exported {len(data):,} items to DataFrame")

        # Create DataFrame
        df = pd.DataFrame(data)

        # Add some useful summary columns
        if not df.empty:
            # Add file status indicators
            df["has_file_path"] = df["file_path"].notna()
            df["file_accessible"] = df["is_local_file"] & df["has_file_path"]

            # Sort by artist, album, track number for logical ordering
            df = df.sort_values(["artist", "album", "track_number"], na_position="last")

            print(
                f"DataFrame created with {len(df)} rows and {len(df.columns)} columns"
            )
            print(f"  Audio files: {(~df['is_video']).sum():,}")
            print(f"  Local files: {df['file_accessible'].sum():,}")
            print(f"  Missing file paths: {(~df['has_file_path']).sum():,}")

        return df

    def save_library_export(self, filepath: str, format: str = "csv", **kwargs) -> None:
        """Export library to various file formats for migration.

        Args:
            filepath: Output file path
            format: Export format ('csv', 'excel', 'json', 'parquet')
            **kwargs: Additional arguments passed to pandas export function
        """
        df = self.export_library_to_dataframe(**kwargs)

        if df.empty:
            print("No data to export.")
            return

        print(f"Saving library export to {filepath} in {format} format...")

        if format.lower() == "csv":
            df.to_csv(filepath, index=False)
        elif format.lower() == "excel":
            df.to_excel(filepath, index=False)
        elif format.lower() == "json":
            df.to_json(filepath, orient="records", indent=2)
        elif format.lower() == "parquet":
            df.to_parquet(filepath, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")

        print(f"Successfully saved {len(df):,} items to {filepath}")

        # Show file size
        try:
            import os

            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"Export file size: {file_size_mb:.2f} MB")
        except:
            pass


def run_comprehensive_demo() -> None:
    """Run a comprehensive demonstration of iTunes Library features."""
    benchmark = LibraryBenchmark()

    print("ITLibrary Bridge - Comprehensive Demo")
    print("=" * 50)

    # Show library summary
    benchmark.show_library_summary()
    print()

    # Run benchmarks
    benchmark.benchmark_library_access()
    print()

    # Demonstrate search
    search_terms = ["Beatles", "Rock", "Love", "2023"]
    benchmark.search_demonstration(search_terms)
    print()

    # Analyze statistics
    benchmark.analyze_library_statistics()

    print("\nDemo completed!")


if __name__ == "__main__":
    run_comprehensive_demo()
