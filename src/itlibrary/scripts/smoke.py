#!/usr/bin/env python3
"""
ITLibrary Bridge Smoke Test Script
Quick validation that the iTunes Library bridge is working correctly
"""

import sys
import traceback

try:
    import itlibrary
    from itlibrary import ITLibrary, ITLibraryError, run_simple_library_example
except ImportError:
    print("✗ FAIL: ITLibrary Bridge not properly installed")
    print("  Please run: make build && make install-dev")
    sys.exit(1)


def test_import():
    """Test that all modules can be imported."""
    print("Testing imports...", end=" ")
    try:
        from itlibrary import ITLibrary, ITLibraryError, MediaItem, Playlist
        from itlibrary.helpers import LibraryBenchmark

        print("✓ PASS")
        return True
    except ImportError as e:
        print(f"✗ FAIL: {e}")
        return False


def test_library_initialization():
    """Test iTunes Library initialization."""
    print("Testing library initialization...", end=" ")
    try:
        library = ITLibrary()
        print("✓ PASS")
        return True
    except ITLibraryError as e:
        print(f"✗ FAIL: {e}")
        return False
    except Exception as e:
        print(f"✗ FAIL: Unexpected error: {e}")
        return False


def test_basic_properties():
    """Test basic library properties."""
    print("Testing basic properties...", end=" ")
    try:
        library = ITLibrary()

        # These should not raise exceptions
        media_count = library.media_items_count
        playlists_count = library.playlists_count
        media_folder = library.media_folder_location
        music_folder = library.music_folder_location

        # Basic sanity checks
        if media_count < 0:
            print("✗ FAIL: Invalid media count")
            return False

        if playlists_count < 0:
            print("✗ FAIL: Invalid playlists count")
            return False

        print("✓ PASS")
        return True

    except ITLibraryError as e:
        print(f"✗ FAIL: {e}")
        return False
    except Exception as e:
        print(f"✗ FAIL: Unexpected error: {e}")
        return False


def test_media_item_access():
    """Test media item access."""
    print("Testing media item access...", end=" ")
    try:
        library = ITLibrary()

        if library.media_items_count == 0:
            print("⚠ SKIP: No media items in library")
            return True

        # Test accessing first item
        item = library.get_media_item(0)

        # Item should exist and have at least some properties
        if item.index != 0:
            print("✗ FAIL: Invalid item index")
            return False

        print("✓ PASS")
        return True

    except ITLibraryError as e:
        print(f"✗ FAIL: {e}")
        return False
    except Exception as e:
        print(f"✗ FAIL: Unexpected error: {e}")
        return False


def test_playlist_access():
    """Test playlist access."""
    print("Testing playlist access...", end=" ")
    try:
        library = ITLibrary()

        if library.playlists_count == 0:
            print("⚠ SKIP: No playlists in library")
            return True

        # Test accessing first playlist
        playlist = library.get_playlist(0)

        # Playlist should exist and have at least some properties
        if playlist.index != 0:
            print("✗ FAIL: Invalid playlist index")
            return False

        print("✓ PASS")
        return True

    except ITLibraryError as e:
        print(f"✗ FAIL: {e}")
        return False
    except Exception as e:
        print(f"✗ FAIL: Unexpected error: {e}")
        return False


def test_search_functionality():
    """Test search functionality."""
    print("Testing search functionality...", end=" ")
    try:
        library = ITLibrary()

        # Test search functions (they should not crash)
        title_results = library.search_by_title("test")
        artist_results = library.search_by_artist("test")

        # Results should be non-negative
        if title_results < 0 or artist_results < 0:
            print("✗ FAIL: Invalid search results")
            return False

        print("✓ PASS")
        return True

    except ITLibraryError as e:
        print(f"✗ FAIL: {e}")
        return False
    except Exception as e:
        print(f"✗ FAIL: Unexpected error: {e}")
        return False


def test_example_function():
    """Test the example function."""
    print("Testing example function...", end=" ")
    try:
        # This should not crash
        run_simple_library_example()
        print("✓ PASS")
        return True
    except ITLibraryError as e:
        print(f"✗ FAIL: {e}")
        return False
    except Exception as e:
        print(f"✗ FAIL: Unexpected error: {e}")
        return False


def main():
    """Run all smoke tests."""
    print("ITLibrary Bridge - Smoke Test")
    print("=" * 40)

    tests = [
        test_import,
        test_library_initialization,
        test_basic_properties,
        test_media_item_access,
        test_playlist_access,
        test_search_functionality,
        test_example_function,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ FAIL: Test crashed: {e}")
            traceback.print_exc()

    print("\nSmoke Test Results:")
    print(f"  Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All smoke tests passed!")
        sys.exit(0)
    else:
        print("❌ Some smoke tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
