#!/usr/bin/env python3
"""
iTunes Library Export Script
Advanced command-line tool for exporting iTunes Library data with filtering, search, and multiple format options
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import pandas as pd

try:
    from pymusiclib.helpers import LibraryBenchmark
    from pymusiclib import ITLibrary, ITLibraryError
except ImportError:
    print("ITLibrary Bridge not properly installed. Please run:")
    print("  make build && make install-dev")
    sys.exit(1)


class LibraryExporter:
    """Advanced iTunes Library exporter with filtering and search capabilities."""

    def __init__(self):
        self.benchmark = LibraryBenchmark()
        self.library: Optional[ITLibrary] = None

    def initialize(self) -> bool:
        """Initialize the iTunes Library connection."""
        return self.benchmark.initialize_library()

    def export_with_filters(
        self,
        output_path: str,
        format_type: str = "csv",
        audio_only: bool = True,
        limit: Optional[int] = None,
        # Filtering options
        artist_filter: Optional[str] = None,
        album_filter: Optional[str] = None,
        genre_filter: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        bitrate_min: Optional[int] = None,
        bitrate_max: Optional[int] = None,
        rating_min: Optional[int] = None,
        date_added_after: Optional[str] = None,
        date_added_before: Optional[str] = None,
        # Search options
        title_search: Optional[str] = None,
        artist_search: Optional[str] = None,
        album_search: Optional[str] = None,
        # Other options
        include_unrated: bool = True,
        local_files_only: bool = False,
        exclude_duplicates: bool = False,
    ) -> pd.DataFrame:
        """Export library with comprehensive filtering and search options.

        Args:
            output_path: Path to save the exported data
            format_type: Export format ('csv', 'excel', 'json', 'parquet')
            audio_only: Filter out video content
            limit: Maximum number of items to process
            artist_filter: Exact artist name to filter by
            album_filter: Exact album name to filter by
            genre_filter: Exact genre to filter by
            year_min: Minimum year (inclusive)
            year_max: Maximum year (inclusive)
            bitrate_min: Minimum bitrate in kbps
            bitrate_max: Maximum bitrate in kbps
            rating_min: Minimum rating (0-100)
            date_added_after: Only include tracks added after this date (YYYY-MM-DD format)
            date_added_before: Only include tracks added before this date (YYYY-MM-DD format)
            title_search: Search term for track titles (case-insensitive)
            artist_search: Search term for artist names (case-insensitive)
            album_search: Search term for album names (case-insensitive)
            include_unrated: Include tracks with no rating
            local_files_only: Only include files with local paths
            exclude_duplicates: Remove duplicate tracks based on title/artist/album

        Returns:
            Filtered pandas DataFrame
        """
        print(f"🎵 Exporting iTunes Library to {format_type.upper()}")
        print("=" * 60)

        if not self.initialize():
            raise ITLibraryError("Failed to initialize iTunes Library")

        # Get the raw DataFrame
        print("📥 Loading library data...")
        df = self.benchmark.export_library_to_dataframe(
            audio_only=audio_only, limit=limit
        )

        if df.empty:
            print("❌ No data found in library")
            return df

        initial_count = len(df)
        print(f"📊 Initial library size: {initial_count:,} items")

        # Apply filters
        print("\n🔍 Applying filters...")

        # Exact match filters
        if artist_filter:
            df = df[df["artist"].str.contains(artist_filter, case=False, na=False)]
            print(f"  • Artist filter '{artist_filter}': {len(df):,} items")

        if album_filter:
            df = df[df["album"].str.contains(album_filter, case=False, na=False)]
            print(f"  • Album filter '{album_filter}': {len(df):,} items")

        if genre_filter:
            df = df[df["genre"].str.contains(genre_filter, case=False, na=False)]
            print(f"  • Genre filter '{genre_filter}': {len(df):,} items")

        # Year range filter
        if year_min is not None:
            df = df[df["year"] >= year_min]
            print(f"  • Year >= {year_min}: {len(df):,} items")

        if year_max is not None:
            df = df[df["year"] <= year_max]
            print(f"  • Year <= {year_max}: {len(df):,} items")

        # Bitrate range filter
        if bitrate_min is not None:
            df = df[df["bitrate_kbps"] >= bitrate_min]
            print(f"  • Bitrate >= {bitrate_min} kbps: {len(df):,} items")

        if bitrate_max is not None:
            df = df[df["bitrate_kbps"] <= bitrate_max]
            print(f"  • Bitrate <= {bitrate_max} kbps: {len(df):,} items")

        # Rating filter
        if rating_min is not None:
            if include_unrated:
                df = df[(df["rating"] >= rating_min) | (df["rating"] == 0)]
                print(
                    f"  • Rating >= {rating_min} (including unrated): {len(df):,} items"
                )
            else:
                df = df[df["rating"] >= rating_min]
                print(f"  • Rating >= {rating_min}: {len(df):,} items")

        # Search filters (case-insensitive substring matching)
        if title_search:
            df = df[df["title"].str.contains(title_search, case=False, na=False)]
            print(f"  • Title search '{title_search}': {len(df):,} items")

        if artist_search:
            df = df[df["artist"].str.contains(artist_search, case=False, na=False)]
            print(f"  • Artist search '{artist_search}': {len(df):,} items")

        if album_search:
            df = df[df["album"].str.contains(album_search, case=False, na=False)]
            print(f"  • Album search '{album_search}': {len(df):,} items")

        # Date filtering
        if date_added_after:
            df = df[df["date_added"] >= date_added_after]
            print(f"  • Added after {date_added_after}: {len(df):,} items")

        if date_added_before:
            df = df[df["date_added"] <= date_added_before]
            print(f"  • Added before {date_added_before}: {len(df):,} items")

        # File accessibility filter
        if local_files_only:
            df = df[df["file_accessible"] == True]
            print(f"  • Local files only: {len(df):,} items")

        # Duplicate removal
        if exclude_duplicates:
            initial_dupe_count = len(df)
            df = df.drop_duplicates(subset=["title", "artist", "album"], keep="first")
            removed_dupes = initial_dupe_count - len(df)
            print(f"  • Removed {removed_dupes:,} duplicates: {len(df):,} items")

        # Final statistics
        filtered_count = len(df)
        print(f"\n📈 Export Summary:")
        print(f"  • Items after filtering: {filtered_count:,} of {initial_count:,}")
        print(f"  • Filter efficiency: {(filtered_count / initial_count) * 100:.1f}%")

        if not df.empty:
            print(f"  • Total file size: {df['file_size_mb'].sum():.1f} MB")
            print(f"  • Unique artists: {df['artist'].nunique()}")
            print(f"  • Unique albums: {df['album'].nunique()}")
            print(f"  • Year range: {df['year'].min()}-{df['year'].max()}")

        # Save the filtered data
        self._save_dataframe(df, output_path, format_type)

        return df

    def _save_dataframe(
        self, df: pd.DataFrame, output_path: str, format_type: str
    ) -> None:
        """Save DataFrame to specified format."""
        if df.empty:
            print("❌ No data to export after filtering")
            return

        print(f"\n💾 Saving to {output_path}...")

        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            if format_type.lower() == "csv":
                df.to_csv(output_path, index=False)
            elif format_type.lower() == "excel":
                df.to_excel(output_path, index=False, engine="openpyxl")
            elif format_type.lower() == "json":
                df.to_json(output_path, orient="records", indent=2)
            elif format_type.lower() == "parquet":
                df.to_parquet(output_path, index=False)
            else:
                raise ValueError(f"Unsupported format: {format_type}")

            # Show file size
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"✅ Successfully exported {len(df):,} items")
            print(f"📁 File: {output_path}")
            print(f"📏 Size: {file_size_mb:.2f} MB")

        except Exception as e:
            print(f"❌ Error saving file: {e}")
            raise

    def show_library_stats(self) -> None:
        """Display comprehensive library statistics for filter planning."""
        print("📊 iTunes Library Statistics")
        print("=" * 50)

        if not self.initialize():
            print("❌ Failed to initialize library")
            return

        # Get sample for analysis
        df = self.benchmark.export_library_to_dataframe(limit=1000)
        if df.empty:
            print("❌ No data found")
            return

        total_items = self.benchmark.library.media_items_count
        sample_size = len(df)

        print(f"📈 Library Overview:")
        print(f"  • Total items: {total_items:,}")
        print(f"  • Sample analyzed: {sample_size:,}")

        print(f"\n🎭 Artists (top 10):")
        top_artists = df["artist"].value_counts().head(10)
        for artist, count in top_artists.items():
            print(f"  • {artist}: {count} tracks")

        print(f"\n💿 Genres (all):")
        genres = df["genre"].value_counts()
        for genre, count in genres.items():
            if pd.notna(genre):
                print(f"  • {genre}: {count} tracks")

        print(f"\n📅 Year Distribution:")
        year_stats = df["year"].describe()
        print(f"  • Range: {int(year_stats['min'])}-{int(year_stats['max'])}")
        print(f"  • Average: {year_stats['mean']:.0f}")

        print(f"\n🎵 Audio Quality:")
        bitrate_stats = df["bitrate_kbps"].describe()
        print(
            f"  • Bitrate range: {int(bitrate_stats['min'])}-{int(bitrate_stats['max'])} kbps"
        )
        print(f"  • Average bitrate: {bitrate_stats['mean']:.0f} kbps")

        print(f"\n📁 File Formats:")
        formats = df["file_extension"].value_counts()
        for fmt, count in formats.items():
            print(f"  • {fmt}: {count} files")

        print(f"\n⭐ Ratings:")
        rating_counts = df["rating"].value_counts().sort_index()
        for rating, count in rating_counts.items():
            if rating == 0:
                print(f"  • Unrated: {count} tracks")
            else:
                print(f"  • {rating}/100: {count} tracks")


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Export iTunes Library to various formats with advanced filtering",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export entire library to CSV
  python export.py library.csv

  # Export only rock music from 2000-2010
  python export.py rock_2000s.csv --genre-filter rock --year-min 2000 --year-max 2010

  # Export high-quality tracks to Excel
  python export.py hq_music.xlsx --format excel --bitrate-min 128

  # Export Beatles albums with search
  python export.py beatles.json --format json --artist-search beatles

  # Show library statistics for planning filters
  python export.py --stats

  # Export local files only, no duplicates
  python export.py clean_library.csv --local-only --no-duplicates --limit 5000

  # Export tracks added in the last year
  python export.py recent_additions.csv --date-added-after 2023-01-01

  # Export tracks added before specific date
  python export.py older_tracks.csv --date-added-before 2020-12-31
        """,
    )

    # Required/positional arguments
    parser.add_argument(
        "output", nargs="?", help="Output file path (required unless using --stats)"
    )

    # Format options
    parser.add_argument(
        "--format",
        "-f",
        choices=["csv", "excel", "json", "parquet"],
        default="csv",
        help="Output format (default: csv)",
    )

    # Basic options
    parser.add_argument(
        "--limit", "-l", type=int, help="Maximum number of items to process"
    )

    parser.add_argument(
        "--include-video",
        action="store_true",
        help="Include video content (default: audio only)",
    )

    # Filtering options
    filter_group = parser.add_argument_group("filtering options")

    filter_group.add_argument(
        "--artist-filter", help="Filter by exact artist name (case-insensitive)"
    )

    filter_group.add_argument(
        "--album-filter", help="Filter by exact album name (case-insensitive)"
    )

    filter_group.add_argument(
        "--genre-filter", help="Filter by exact genre (case-insensitive)"
    )

    filter_group.add_argument("--year-min", type=int, help="Minimum year (inclusive)")

    filter_group.add_argument("--year-max", type=int, help="Maximum year (inclusive)")

    filter_group.add_argument("--bitrate-min", type=int, help="Minimum bitrate in kbps")

    filter_group.add_argument("--bitrate-max", type=int, help="Maximum bitrate in kbps")

    filter_group.add_argument("--rating-min", type=int, help="Minimum rating (0-100)")

    filter_group.add_argument(
        "--date-added-after",
        help="Only include tracks added after this date (YYYY-MM-DD)",
    )

    filter_group.add_argument(
        "--date-added-before",
        help="Only include tracks added before this date (YYYY-MM-DD)",
    )

    # Search options
    search_group = parser.add_argument_group("search options")

    search_group.add_argument(
        "--title-search", help="Search track titles (case-insensitive substring)"
    )

    search_group.add_argument(
        "--artist-search", help="Search artist names (case-insensitive substring)"
    )

    search_group.add_argument(
        "--album-search", help="Search album names (case-insensitive substring)"
    )

    # Advanced options
    advanced_group = parser.add_argument_group("advanced options")

    advanced_group.add_argument(
        "--exclude-unrated",
        action="store_true",
        help="Exclude tracks with no rating when using --rating-min",
    )

    advanced_group.add_argument(
        "--local-only",
        action="store_true",
        help="Only include files with accessible local paths",
    )

    advanced_group.add_argument(
        "--no-duplicates",
        action="store_true",
        help="Remove duplicate tracks (by title/artist/album)",
    )

    # Utility options
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show library statistics and exit (for planning filters)",
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    return parser


def main():
    """Main function for command-line usage."""
    parser = create_parser()
    args = parser.parse_args()

    # Validate arguments
    if not args.stats and not args.output:
        parser.error("Output file is required unless using --stats")

    exporter = LibraryExporter()

    try:
        # Show stats and exit if requested
        if args.stats:
            exporter.show_library_stats()
            return

        # Perform export with filters
        df = exporter.export_with_filters(
            output_path=args.output,
            format_type=args.format,
            audio_only=not args.include_video,
            limit=args.limit,
            # Filters
            artist_filter=args.artist_filter,
            album_filter=args.album_filter,
            genre_filter=args.genre_filter,
            year_min=args.year_min,
            year_max=args.year_max,
            bitrate_min=args.bitrate_min,
            bitrate_max=args.bitrate_max,
            rating_min=args.rating_min,
            date_added_after=args.date_added_after,
            date_added_before=args.date_added_before,
            # Search
            title_search=args.title_search,
            artist_search=args.artist_search,
            album_search=args.album_search,
            # Advanced
            include_unrated=not args.exclude_unrated,
            local_files_only=args.local_only,
            exclude_duplicates=args.no_duplicates,
        )

        if not df.empty:
            print(f"\n🎉 Export completed successfully!")
            print(f"📊 Final dataset: {len(df):,} tracks")
        else:
            print(f"\n⚠️  No tracks matched the specified filters")
            sys.exit(1)

    except ITLibraryError as e:
        print(f"❌ iTunes Library Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
