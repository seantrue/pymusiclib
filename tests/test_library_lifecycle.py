"""
Tests for iTunes Library lifecycle management and resource handling.

These tests are designed to reveal problems with library connection cleanup,
resource leaks, and race conditions in library management.
"""

import gc
import threading
import time
import weakref
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

import pytest

try:
    from musiclib import ITLibrary, ITLibraryError, MediaItem, Playlist
except ImportError:
    pytest.skip("MusicLib not available", allow_module_level=True)


class TestLibraryLifecycle:
    """Test library lifecycle management and cleanup."""

    def test_library_cleanup_on_deletion(self):
        """Test that iTunes Library connections are properly cleaned up when Python objects are deleted."""
        # Create library instance
        library = ITLibrary()

        # Store weak reference to track when it's garbage collected
        weak_ref = weakref.ref(library)

        # Use library briefly
        media_count = library.media_items_count

        # Delete library instance
        del library

        # Force garbage collection
        gc.collect()

        # Weak reference should be dead (object was cleaned up)
        assert weak_ref() is None

    def test_multiple_library_instances(self):
        """Test creating and managing multiple library instances."""
        libraries = []

        # Create multiple instances
        for i in range(5):
            library = ITLibrary()
            libraries.append(library)

        # All should work independently
        for library in libraries:
            count = library.media_items_count
            assert isinstance(count, int)
            assert count >= 0

        # Clean up all instances
        for library in libraries:
            del library

        gc.collect()

    def test_library_reuse_after_cleanup(self):
        """Test that we can create new library instances after cleanup."""
        # Create and use first library
        library1 = ITLibrary()
        count1 = library1.media_items_count
        del library1

        gc.collect()

        # Create and use second library
        library2 = ITLibrary()
        count2 = library2.media_items_count

        # Should get same results
        assert count1 == count2

        del library2

    def test_media_item_lifecycle(self):
        """Test that media items are properly cleaned up."""
        library = ITLibrary()
        media_count = library.media_items_count

        if media_count == 0:
            pytest.skip("No media items in library")

        # Create multiple media items
        items = []
        for i in range(min(10, media_count)):
            item = library.get_media_item(i)
            items.append(item)

        # Store weak references
        weak_refs = [weakref.ref(item) for item in items]

        # Clear items
        del items
        gc.collect()

        # Weak references should be cleared
        for weak_ref in weak_refs:
            assert weak_ref() is None

    def test_playlist_lifecycle(self):
        """Test that playlists are properly cleaned up."""
        library = ITLibrary()
        playlists_count = library.playlists_count

        if playlists_count == 0:
            pytest.skip("No playlists in library")

        # Create multiple playlists
        playlists = []
        for i in range(min(5, playlists_count)):
            playlist = library.get_playlist(i)
            playlists.append(playlist)

        # Store weak references
        weak_refs = [weakref.ref(playlist) for playlist in playlists]

        # Clear playlists
        del playlists
        gc.collect()

        # Weak references should be cleared
        for weak_ref in weak_refs:
            assert weak_ref() is None


class TestConcurrentAccess:
    """Test concurrent access to iTunes Library."""

    def test_concurrent_library_creation(self):
        """Test creating library instances concurrently."""

        def create_library():
            library = ITLibrary()
            count = library.media_items_count
            return count

        # Run concurrent library creation
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_library) for _ in range(10)]
            results = [future.result() for future in as_completed(futures)]

        # All should return the same count
        assert all(result == results[0] for result in results)

    def test_concurrent_media_access(self):
        """Test concurrent media item access."""
        library = ITLibrary()
        media_count = library.media_items_count

        if media_count == 0:
            pytest.skip("No media items in library")

        def access_media_items(start_idx, count):
            items = []
            for i in range(start_idx, min(start_idx + count, media_count)):
                item = library.get_media_item(i)
                items.append(item.title)
            return items

        # Run concurrent media access
        batch_size = min(10, media_count // 3)
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(access_media_items, i * batch_size, batch_size)
                for i in range(3)
            ]
            results = [future.result() for future in as_completed(futures)]

        # Should not crash and should return valid results
        for result in results:
            assert isinstance(result, list)

    @pytest.mark.slow
    def test_stress_library_access(self):
        """Stress test library access patterns."""
        library = ITLibrary()

        def stress_worker():
            for _ in range(100):
                # Rapid access to various properties
                count = library.media_items_count
                playlists = library.playlists_count
                folder = library.media_folder_location

                # Search operations
                library.search_by_title("test")
                library.search_by_artist("test")

                time.sleep(0.001)  # Small delay

        # Run multiple stress workers
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=stress_worker)
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()


class TestResourceLimits:
    """Test resource limits and error conditions."""

    def test_large_batch_access(self):
        """Test accessing large numbers of items."""
        library = ITLibrary()
        media_count = library.media_items_count

        if media_count < 100:
            pytest.skip("Not enough media items for batch test")

        # Access items in large batches
        batch_size = min(100, media_count)

        start_time = time.time()
        for i in range(0, batch_size, 10):
            batch = []
            for j in range(i, min(i + 10, batch_size)):
                item = library.get_media_item(j)
                batch.append(item)
            # Process batch
            titles = [item.title for item in batch]

        elapsed = time.time() - start_time

        # Should complete within reasonable time
        assert elapsed < 30.0  # 30 seconds max

    def test_repeated_initialization(self):
        """Test repeated library initialization and cleanup."""
        for i in range(20):
            library = ITLibrary()
            count = library.media_items_count
            del library
            gc.collect()

        # Should not crash or leak resources

    def test_error_handling_during_cleanup(self):
        """Test that cleanup works even when errors occur."""
        library = ITLibrary()

        # Try to access invalid indices to trigger errors
        try:
            library.get_media_item(-1)
        except ITLibraryError:
            pass  # Expected

        try:
            library.get_playlist(-1)
        except ITLibraryError:
            pass  # Expected

        # Library should still clean up properly
        del library
        gc.collect()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
