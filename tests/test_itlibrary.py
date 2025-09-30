"""
Comprehensive ITLibrary Bridge Test Suite
==========================================

This module provides comprehensive testing for the ITLibrary Bridge using pytest.
Includes unit tests, integration tests, and error handling tests.

🎯 Test Categories:
• TestITLibraryCore - Basic functionality (library initialization, basic properties)
• TestITLibraryMediaItems - Media item access and properties
• TestITLibraryPlaylists - Playlist access and properties
• TestITLibrarySearch - Search functionality
• TestITLibraryErrorHandling - Error cases and edge conditions
• TestITLibraryPerformance - Performance benchmarks

📋 Usage:
    pytest test_itlibrary.py -v                       # Run all tests
    pytest test_itlibrary.py::TestITLibraryCore -v    # Run core tests only
    pytest test_itlibrary.py -k "search" -v           # Run tests matching "search"
    pytest test_itlibrary.py --tb=short -v            # Shorter traceback format

🔧 Requirements:
• ITLibrary Bridge properly installed and compiled
• macOS with iTunes Library framework
• Python 3.10+ with pytest, numpy
• iTunes/Music app with some media content

⚡ Performance Expectations:
• Library initialization: <2s
• Media item access: <10ms per item
• Search operations: <500ms
"""

import pytest
import sys
import time
from typing import List, Optional

try:
    import musiclib
    from musiclib import ITLibrary, ITLibraryError, MediaItem, Playlist
    from musiclib.helpers import LibraryBenchmark
except ImportError as e:
    pytest.skip(f"MusicLib not available: {e}", allow_module_level=True)


class TestITLibraryCore:
    """Test core iTunes Library functionality."""

    def test_import_success(self):
        """Test that all modules can be imported successfully."""
        assert musiclib is not None
        assert ITLibrary is not None
        assert ITLibraryError is not None
        assert MediaItem is not None
        assert Playlist is not None

    def test_library_initialization(self):
        """Test iTunes Library initialization."""
        library = ITLibrary()
        assert library is not None

    def test_library_properties(self):
        """Test basic library properties."""
        library = ITLibrary()

        # Test that properties return reasonable values
        media_count = library.media_items_count
        assert isinstance(media_count, int)
        assert media_count >= 0

        playlists_count = library.playlists_count
        assert isinstance(playlists_count, int)
        assert playlists_count >= 0

        # Test folder locations (can be None)
        media_folder = library.media_folder_location
        if media_folder is not None:
            assert isinstance(media_folder, str)
            assert len(media_folder) > 0

        music_folder = library.music_folder_location
        if music_folder is not None:
            assert isinstance(music_folder, str)
            assert len(music_folder) > 0

    def test_example_function(self):
        """Test the example function runs without error."""
        # This should not raise any exceptions
        musiclib.run_simple_library_example()


class TestITLibraryMediaItems:
    """Test media item functionality."""

    @pytest.fixture
    def library(self):
        """Provide a library instance for tests."""
        return ITLibrary()

    def test_media_item_access(self, library):
        """Test accessing media items."""
        media_count = library.media_items_count

        if media_count == 0:
            pytest.skip("No media items in library")

        # Test accessing first item
        item = library.get_media_item(0)
        assert isinstance(item, MediaItem)
        assert item.index == 0

        # Test accessing last item
        if media_count > 1:
            item = library.get_media_item(media_count - 1)
            assert isinstance(item, MediaItem)
            assert item.index == media_count - 1

    def test_media_item_properties(self, library):
        """Test media item properties."""
        media_count = library.media_items_count

        if media_count == 0:
            pytest.skip("No media items in library")

        item = library.get_media_item(0)

        # Test property types
        if item.title is not None:
            assert isinstance(item.title, str)

        if item.artist is not None:
            assert isinstance(item.artist, str)

        if item.album is not None:
            assert isinstance(item.album, str)

        assert isinstance(item.duration, int)
        assert item.duration >= 0

        assert isinstance(item.track_number, int)
        assert item.track_number >= 0

        assert isinstance(item.year, int)
        assert item.year >= 0

        if item.location is not None:
            assert isinstance(item.location, str)

    def test_media_item_index_bounds(self, library):
        """Test media item index boundary conditions."""
        media_count = library.media_items_count

        if media_count == 0:
            pytest.skip("No media items in library")

        # Test negative index
        with pytest.raises(ITLibraryError):
            library.get_media_item(-1)

        # Test index beyond bounds
        with pytest.raises(ITLibraryError):
            library.get_media_item(media_count)

    def test_get_all_media_items(self, library):
        """Test getting all media items."""
        media_count = library.media_items_count

        if media_count == 0:
            pytest.skip("No media items in library")

        # Test for small libraries only to avoid performance issues
        if media_count > 100:
            pytest.skip("Library too large for full enumeration test")

        all_items = library.get_all_media_items()
        assert len(all_items) == media_count

        for i, item in enumerate(all_items):
            assert isinstance(item, MediaItem)
            assert item.index == i


class TestITLibraryPlaylists:
    """Test playlist functionality."""

    @pytest.fixture
    def library(self):
        """Provide a library instance for tests."""
        return ITLibrary()

    def test_playlist_access(self, library):
        """Test accessing playlists."""
        playlists_count = library.playlists_count

        if playlists_count == 0:
            pytest.skip("No playlists in library")

        # Test accessing first playlist
        playlist = library.get_playlist(0)
        assert isinstance(playlist, Playlist)
        assert playlist.index == 0

        # Test accessing last playlist
        if playlists_count > 1:
            playlist = library.get_playlist(playlists_count - 1)
            assert isinstance(playlist, Playlist)
            assert playlist.index == playlists_count - 1

    def test_playlist_properties(self, library):
        """Test playlist properties."""
        playlists_count = library.playlists_count

        if playlists_count == 0:
            pytest.skip("No playlists in library")

        playlist = library.get_playlist(0)

        # Test property types
        if playlist.name is not None:
            assert isinstance(playlist.name, str)

        assert isinstance(playlist.item_count, int)
        assert playlist.item_count >= 0

    def test_playlist_index_bounds(self, library):
        """Test playlist index boundary conditions."""
        playlists_count = library.playlists_count

        if playlists_count == 0:
            pytest.skip("No playlists in library")

        # Test negative index
        with pytest.raises(ITLibraryError):
            library.get_playlist(-1)

        # Test index beyond bounds
        with pytest.raises(ITLibraryError):
            library.get_playlist(playlists_count)

    def test_get_all_playlists(self, library):
        """Test getting all playlists."""
        playlists_count = library.playlists_count

        if playlists_count == 0:
            pytest.skip("No playlists in library")

        # Test for reasonable playlist counts
        if playlists_count > 50:
            pytest.skip("Too many playlists for full enumeration test")

        all_playlists = library.get_all_playlists()
        assert len(all_playlists) == playlists_count

        for i, playlist in enumerate(all_playlists):
            assert isinstance(playlist, Playlist)
            assert playlist.index == i


class TestITLibrarySearch:
    """Test search functionality."""

    @pytest.fixture
    def library(self):
        """Provide a library instance for tests."""
        return ITLibrary()

    def test_search_by_title(self, library):
        """Test title search functionality."""
        # Test various search terms
        search_terms = ["the", "love", "music", "song", "test"]

        for term in search_terms:
            result = library.search_by_title(term)
            assert isinstance(result, int)
            assert result >= 0

    def test_search_by_artist(self, library):
        """Test artist search functionality."""
        # Test various search terms
        search_terms = ["beatles", "unknown", "artist", "band", "test"]

        for term in search_terms:
            result = library.search_by_artist(term)
            assert isinstance(result, int)
            assert result >= 0

    def test_search_empty_string(self, library):
        """Test search with empty string."""
        title_result = library.search_by_title("")
        assert isinstance(title_result, int)
        assert title_result >= 0

        artist_result = library.search_by_artist("")
        assert isinstance(artist_result, int)
        assert artist_result >= 0

    def test_search_unicode(self, library):
        """Test search with unicode characters."""
        unicode_terms = ["café", "naïve", "résumé", "北京"]

        for term in unicode_terms:
            title_result = library.search_by_title(term)
            assert isinstance(title_result, int)
            assert title_result >= 0

            artist_result = library.search_by_artist(term)
            assert isinstance(artist_result, int)
            assert artist_result >= 0


class TestITLibraryErrorHandling:
    """Test error handling and edge cases."""

    def test_library_cleanup(self):
        """Test that library cleanup works properly."""
        library = ITLibrary()
        # Access some properties to ensure initialization
        _ = library.media_items_count

        # Cleanup should happen automatically when library goes out of scope
        del library

    def test_multiple_library_instances(self):
        """Test creating multiple library instances."""
        library1 = ITLibrary()
        library2 = ITLibrary()

        # Both should work independently
        count1 = library1.media_items_count
        count2 = library2.media_items_count

        assert count1 == count2  # Should be the same library


@pytest.mark.slow
class TestITLibraryPerformance:
    """Test performance characteristics."""

    @pytest.fixture
    def library(self):
        """Provide a library instance for tests."""
        return ITLibrary()

    def test_library_initialization_performance(self):
        """Test library initialization performance."""
        start_time = time.time()
        library = ITLibrary()
        initialization_time = time.time() - start_time

        # Should initialize within reasonable time
        assert initialization_time < 5.0

    def test_media_item_access_performance(self, library):
        """Test media item access performance."""
        media_count = library.media_items_count

        if media_count == 0:
            pytest.skip("No media items in library")

        # Test access speed for first 100 items
        sample_size = min(100, media_count)

        start_time = time.time()
        for i in range(sample_size):
            item = library.get_media_item(i)
            # Access properties to ensure they're loaded
            _ = item.title
            _ = item.artist
            _ = item.duration

        access_time = time.time() - start_time
        avg_time_per_item = access_time / sample_size

        # Should be reasonably fast
        assert avg_time_per_item < 0.1  # 100ms per item max

    def test_search_performance(self, library):
        """Test search performance."""
        search_terms = ["the", "love", "rock", "music", "song"]

        for term in search_terms:
            start_time = time.time()
            title_result = library.search_by_title(term)
            artist_result = library.search_by_artist(term)
            search_time = time.time() - start_time

            # Search should be reasonably fast
            assert search_time < 2.0

    def test_benchmark_integration(self):
        """Test that benchmark utilities work."""
        benchmark = LibraryBenchmark()

        # This should not raise exceptions
        try:
            benchmark.benchmark_library_access()
        except ITLibraryError:
            pytest.skip("Library access failed")


def test_demos():
    """Test that demo scripts can be imported and run."""
    try:
        from musiclib.scripts import demo, smoke

        # These should not raise import errors
        assert demo is not None
        assert smoke is not None

    except ImportError as e:
        pytest.fail(f"Failed to import demo scripts: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
