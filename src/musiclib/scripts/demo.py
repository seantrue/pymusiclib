#!/usr/bin/env python3
"""
ITLibrary Bridge Demo Script
Comprehensive demonstration of iTunes Library access functionality
"""

import argparse
import sys
import traceback
from typing import List

try:
    from musiclib.helpers import LibraryBenchmark, run_comprehensive_demo
    from musiclib import ITLibrary, ITLibraryError
except ImportError:
    print("MusicLib not properly installed. Please run:")
    print("  make build && make install-dev")
    sys.exit(1)


def demo_basic_access():
    """Demonstrate basic iTunes Library access."""
    print("=== Basic Library Access Demo ===")

    try:
        library = ITLibrary()

        print(f"✓ Successfully connected to iTunes Library")
        print(f"  Media items: {library.media_items_count:,}")
        print(f"  Playlists: {library.playlists_count:,}")
        print(f"  Media folder: {library.media_folder_location}")
        print(f"  Music folder: {library.music_folder_location}")

        # Show first few items
        print("\nFirst 3 media items:")
        for i in range(min(3, library.media_items_count)):
            item = library.get_media_item(i)
            duration_str = (
                f"{item.duration // 60}:{item.duration % 60:02d}"
                if item.duration > 0
                else "unknown"
            )
            print(
                f"  {i + 1}. {item.title} - {item.artist} [{item.album}] ({duration_str})"
            )

    except ITLibraryError as e:
        print(f"✗ iTunes Library Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        traceback.print_exc()
        return False

    return True


def demo_search():
    """Demonstrate search functionality."""
    print("\n=== Search Demo ===")

    try:
        library = ITLibrary()

        # Common search terms
        search_terms = ["love", "rock", "the", "2020"]

        for term in search_terms:
            title_matches = library.search_by_title(term)
            artist_matches = library.search_by_artist(term)
            print(f"'{term}': {title_matches} titles, {artist_matches} artists")

    except ITLibraryError as e:
        print(f"✗ iTunes Library Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

    return True


def demo_playlists():
    """Demonstrate playlist access."""
    print("\n=== Playlists Demo ===")

    try:
        library = ITLibrary()

        print(f"Total playlists: {library.playlists_count}")
        print("\nFirst 5 playlists:")

        for i in range(min(5, library.playlists_count)):
            playlist = library.get_playlist(i)
            print(f"  {i + 1}. {playlist.name} ({playlist.item_count} items)")

    except ITLibraryError as e:
        print(f"✗ iTunes Library Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

    return True


def demo_benchmarks():
    """Run performance benchmarks."""
    print("\n=== Performance Benchmarks ===")

    try:
        benchmark = LibraryBenchmark()
        benchmark.benchmark_library_access()

    except ITLibraryError as e:
        print(f"✗ iTunes Library Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

    return True


def demo_statistics():
    """Analyze library statistics."""
    print("\n=== Library Statistics ===")

    try:
        benchmark = LibraryBenchmark()
        benchmark.analyze_library_statistics()

    except ITLibraryError as e:
        print(f"✗ iTunes Library Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

    return True


def main():
    """Main demo function with command line options."""
    parser = argparse.ArgumentParser(description="ITLibrary Bridge Demo")
    parser.add_argument(
        "--demos",
        choices=["basic", "search", "playlists", "benchmarks", "statistics", "all"],
        default="all",
        help="Which demos to run",
    )

    args = parser.parse_args()

    print("ITLibrary Bridge - Demo Script")
    print("=" * 50)

    demos = {
        "basic": demo_basic_access,
        "search": demo_search,
        "playlists": demo_playlists,
        "benchmarks": demo_benchmarks,
        "statistics": demo_statistics,
    }

    success_count = 0
    total_count = 0

    if args.demos == "all":
        # Run comprehensive demo
        try:
            run_comprehensive_demo()
            print("✓ Comprehensive demo completed successfully")
            success_count = 1
            total_count = 1
        except Exception as e:
            print(f"✗ Comprehensive demo failed: {e}")
            traceback.print_exc()
            total_count = 1
    else:
        # Run specific demo
        demo_func = demos[args.demos]
        total_count = 1
        if demo_func():
            success_count = 1
            print(f"✓ {args.demos} demo completed successfully")
        else:
            print(f"✗ {args.demos} demo failed")

    print(f"\nDemo Results: {success_count}/{total_count} successful")

    if success_count == total_count:
        print("🎉 All demos completed successfully!")
        sys.exit(0)
    else:
        print("❌ Some demos failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
