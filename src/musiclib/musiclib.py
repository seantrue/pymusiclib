from __future__ import annotations

import ctypes
import os
import threading
import weakref
from ctypes import c_bool, c_char_p, c_int32, c_void_p
from dataclasses import dataclass
from typing import Any, List, Optional

import numpy as np


# Public error type
class ITLibraryError(Exception):
    pass


# Internal FFI loader
_itlib = None
_library_lock = threading.Lock()


def _load_itlibrary() -> ctypes.CDLL:
    """Load the iTunes Library bridge dynamic library."""
    # Prefer the packaged dylib sitting next to this file
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    local_path = os.path.join(pkg_dir, "libitlibrary.dylib")
    if os.path.exists(local_path):
        return ctypes.CDLL(local_path)
    # Fallback to default loader if needed
    try:
        return ctypes.CDLL("libitlibrary.dylib")
    except OSError as e:
        raise ITLibraryError(
            "Failed to load libitlibrary.dylib. Ensure it is built and on your DYLD_LIBRARY_PATH"
        ) from e


def _setup_function_signatures(lib: ctypes.CDLL) -> None:
    """Setup function signatures for the iTunes Library bridge."""
    # Error handling
    lib.itlib_get_last_error.restype = ctypes.POINTER(ctypes.c_char)

    # Library management
    lib.itlib_initialize.restype = c_bool
    lib.itlib_cleanup.restype = None
    lib.itlib_is_initialized.restype = c_bool

    # Library information
    lib.itlib_get_media_folder_location.restype = ctypes.POINTER(ctypes.c_char)
    lib.itlib_get_music_folder_location.restype = ctypes.POINTER(ctypes.c_char)

    # Media items
    lib.itlib_get_media_items_count.restype = c_int32
    lib.itlib_get_media_item_title.argtypes = [c_int32]
    lib.itlib_get_media_item_title.restype = ctypes.POINTER(ctypes.c_char)
    lib.itlib_get_media_item_artist.argtypes = [c_int32]
    lib.itlib_get_media_item_artist.restype = ctypes.POINTER(ctypes.c_char)
    lib.itlib_get_media_item_album.argtypes = [c_int32]
    lib.itlib_get_media_item_album.restype = ctypes.POINTER(ctypes.c_char)
    lib.itlib_get_media_item_duration.argtypes = [c_int32]
    lib.itlib_get_media_item_duration.restype = c_int32
    lib.itlib_get_media_item_track_number.argtypes = [c_int32]
    lib.itlib_get_media_item_track_number.restype = c_int32
    lib.itlib_get_media_item_year.argtypes = [c_int32]
    lib.itlib_get_media_item_year.restype = c_int32
    lib.itlib_get_media_item_location.argtypes = [c_int32]
    lib.itlib_get_media_item_location.restype = ctypes.POINTER(ctypes.c_char)

    # Extended media item metadata
    lib.itlib_get_media_item_genre.argtypes = [c_int32]
    lib.itlib_get_media_item_genre.restype = ctypes.POINTER(ctypes.c_char)
    lib.itlib_get_media_item_bitrate.argtypes = [c_int32]
    lib.itlib_get_media_item_bitrate.restype = ctypes.c_int64
    lib.itlib_get_media_item_sample_rate.argtypes = [c_int32]
    lib.itlib_get_media_item_sample_rate.restype = ctypes.c_int64
    lib.itlib_get_media_item_file_size.argtypes = [c_int32]
    lib.itlib_get_media_item_file_size.restype = ctypes.c_int64
    lib.itlib_get_media_item_kind.argtypes = [c_int32]
    lib.itlib_get_media_item_kind.restype = ctypes.POINTER(ctypes.c_char)
    lib.itlib_get_media_item_album_artist.argtypes = [c_int32]
    lib.itlib_get_media_item_album_artist.restype = ctypes.POINTER(ctypes.c_char)
    lib.itlib_get_media_item_total_time_ms.argtypes = [c_int32]
    lib.itlib_get_media_item_total_time_ms.restype = ctypes.c_int64
    lib.itlib_get_media_item_play_count.argtypes = [c_int32]
    lib.itlib_get_media_item_play_count.restype = c_int32
    lib.itlib_get_media_item_rating.argtypes = [c_int32]
    lib.itlib_get_media_item_rating.restype = c_int32
    lib.itlib_get_media_item_is_video.argtypes = [c_int32]
    lib.itlib_get_media_item_is_video.restype = ctypes.c_bool
    lib.itlib_get_media_item_date_added.argtypes = [c_int32]
    lib.itlib_get_media_item_date_added.restype = ctypes.c_int64

    # Playlists
    lib.itlib_get_playlists_count.restype = c_int32
    lib.itlib_get_playlist_name.argtypes = [c_int32]
    lib.itlib_get_playlist_name.restype = ctypes.POINTER(ctypes.c_char)
    lib.itlib_get_playlist_items_count.argtypes = [c_int32]
    lib.itlib_get_playlist_items_count.restype = c_int32

    # Search functions
    lib.itlib_search_media_items_by_title.argtypes = [c_char_p]
    lib.itlib_search_media_items_by_title.restype = c_int32
    lib.itlib_search_media_items_by_artist.argtypes = [c_char_p]
    lib.itlib_search_media_items_by_artist.restype = c_int32


def _get_itlibrary() -> ctypes.CDLL:
    """Get the global iTunes Library instance, initializing if needed."""
    global _itlib
    if _itlib is None:
        with _library_lock:
            if _itlib is None:
                _itlib = _load_itlibrary()
                _setup_function_signatures(_itlib)
    return _itlib


def _check_error() -> None:
    """Check for and raise any pending iTunes Library errors."""
    lib = _get_itlibrary()
    error_ptr = lib.itlib_get_last_error()
    if error_ptr:
        error_msg = ctypes.string_at(error_ptr).decode("utf-8")
        raise ITLibraryError(error_msg)


@dataclass
class MediaItem:
    """Represents a media item in the iTunes Library."""

    index: int
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    duration: int = 0  # in seconds
    track_number: int = 0
    year: int = 0
    location: Optional[str] = None
    # Extended metadata for media migration
    genre: Optional[str] = None
    bitrate: int = 0  # in kbps
    sample_rate: int = 0  # in Hz
    file_size: int = 0  # in bytes
    kind: Optional[str] = None  # file format/codec
    album_artist: Optional[str] = None
    total_time_ms: int = 0  # in milliseconds (more precise than duration)
    play_count: int = 0
    rating: int = 0  # 0-100
    is_video: bool = False
    date_added: Optional[str] = None  # ISO format date string

    @classmethod
    def from_index(cls, index: int) -> "MediaItem":
        """Create a MediaItem from its index in the library."""
        lib = _get_itlibrary()

        title_ptr = lib.itlib_get_media_item_title(index)
        title = ctypes.string_at(title_ptr).decode("utf-8") if title_ptr else None

        artist_ptr = lib.itlib_get_media_item_artist(index)
        artist = ctypes.string_at(artist_ptr).decode("utf-8") if artist_ptr else None

        album_ptr = lib.itlib_get_media_item_album(index)
        album = ctypes.string_at(album_ptr).decode("utf-8") if album_ptr else None

        duration = lib.itlib_get_media_item_duration(index)
        track_number = lib.itlib_get_media_item_track_number(index)
        year = lib.itlib_get_media_item_year(index)

        location_ptr = lib.itlib_get_media_item_location(index)
        location = (
            ctypes.string_at(location_ptr).decode("utf-8") if location_ptr else None
        )

        # Extended metadata
        genre_ptr = lib.itlib_get_media_item_genre(index)
        genre = ctypes.string_at(genre_ptr).decode("utf-8") if genre_ptr else None

        bitrate = lib.itlib_get_media_item_bitrate(index)
        sample_rate = lib.itlib_get_media_item_sample_rate(index)
        file_size = lib.itlib_get_media_item_file_size(index)

        kind_ptr = lib.itlib_get_media_item_kind(index)
        kind = ctypes.string_at(kind_ptr).decode("utf-8") if kind_ptr else None

        album_artist_ptr = lib.itlib_get_media_item_album_artist(index)
        album_artist = (
            ctypes.string_at(album_artist_ptr).decode("utf-8")
            if album_artist_ptr
            else None
        )

        total_time_ms = lib.itlib_get_media_item_total_time_ms(index)
        play_count = lib.itlib_get_media_item_play_count(index)
        rating = lib.itlib_get_media_item_rating(index)
        is_video = lib.itlib_get_media_item_is_video(index)

        # Get date added (Unix timestamp)
        date_added_timestamp = lib.itlib_get_media_item_date_added(index)
        date_added = None
        if date_added_timestamp > 0:
            import datetime

            date_added = datetime.datetime.fromtimestamp(
                date_added_timestamp
            ).isoformat()

        return cls(
            index=index,
            title=title,
            artist=artist,
            album=album,
            duration=duration,
            track_number=track_number,
            year=year,
            location=location,
            genre=genre,
            bitrate=bitrate if bitrate >= 0 else 0,
            sample_rate=sample_rate if sample_rate >= 0 else 0,
            file_size=file_size if file_size >= 0 else 0,
            kind=kind,
            album_artist=album_artist,
            total_time_ms=total_time_ms if total_time_ms >= 0 else 0,
            play_count=play_count if play_count >= 0 else 0,
            rating=rating if rating >= 0 else 0,
            is_video=is_video,
            date_added=date_added,
        )


@dataclass
class Playlist:
    """Represents a playlist in the iTunes Library."""

    index: int
    name: Optional[str] = None
    item_count: int = 0

    @classmethod
    def from_index(cls, index: int) -> "Playlist":
        """Create a Playlist from its index in the library."""
        lib = _get_itlibrary()

        name_ptr = lib.itlib_get_playlist_name(index)
        name = ctypes.string_at(name_ptr).decode("utf-8") if name_ptr else None

        item_count = lib.itlib_get_playlist_items_count(index)

        return cls(index=index, name=name, item_count=item_count)


class ITLibrary:
    """Main interface to the iTunes Library."""

    def __init__(self):
        """Initialize connection to iTunes Library."""
        self._lib = _get_itlibrary()
        if not self._lib.itlib_initialize():
            _check_error()
            raise ITLibraryError("Failed to initialize iTunes Library")

    def __del__(self):
        """Clean up iTunes Library connection."""
        if hasattr(self, "_lib") and self._lib:
            self._lib.itlib_cleanup()

    @property
    def media_folder_location(self) -> Optional[str]:
        """Get the location of the iTunes media folder."""
        location_ptr = self._lib.itlib_get_media_folder_location()
        if location_ptr:
            return ctypes.string_at(location_ptr).decode("utf-8")
        return None

    @property
    def music_folder_location(self) -> Optional[str]:
        """Get the location of the iTunes music folder."""
        location_ptr = self._lib.itlib_get_music_folder_location()
        if location_ptr:
            return ctypes.string_at(location_ptr).decode("utf-8")
        return None

    @property
    def media_items_count(self) -> int:
        """Get the total number of media items in the library."""
        count = self._lib.itlib_get_media_items_count()
        if count < 0:
            _check_error()
        return count

    @property
    def playlists_count(self) -> int:
        """Get the total number of playlists in the library."""
        count = self._lib.itlib_get_playlists_count()
        if count < 0:
            _check_error()
        return count

    def get_media_item(self, index: int) -> MediaItem:
        """Get a media item by its index."""
        if index < 0 or index >= self.media_items_count:
            raise ITLibraryError(f"Media item index {index} out of range")
        return MediaItem.from_index(index)

    def get_playlist(self, index: int) -> Playlist:
        """Get a playlist by its index."""
        if index < 0 or index >= self.playlists_count:
            raise ITLibraryError(f"Playlist index {index} out of range")
        return Playlist.from_index(index)

    def get_all_media_items(self) -> List[MediaItem]:
        """Get all media items in the library."""
        return [self.get_media_item(i) for i in range(self.media_items_count)]

    def get_all_playlists(self) -> List[Playlist]:
        """Get all playlists in the library."""
        return [self.get_playlist(i) for i in range(self.playlists_count)]

    def search_by_title(self, search_term: str) -> int:
        """Search for media items by title. Returns count of matches."""
        search_bytes = search_term.encode("utf-8")
        count = self._lib.itlib_search_media_items_by_title(search_bytes)
        if count < 0:
            _check_error()
        return count

    def search_by_artist(self, search_term: str) -> int:
        """Search for media items by artist. Returns count of matches."""
        search_bytes = search_term.encode("utf-8")
        count = self._lib.itlib_search_media_items_by_artist(search_bytes)
        if count < 0:
            _check_error()
        return count


def run_simple_library_example() -> None:
    """Run a simple example demonstrating iTunes Library access."""
    try:
        print("iTunes Library Bridge Example")
        print("=" * 40)

        # Initialize library
        library = ITLibrary()
        print(f"Successfully initialized iTunes Library")

        # Show library info
        print(f"Media folder: {library.media_folder_location}")
        print(f"Music folder: {library.music_folder_location}")
        print(f"Total media items: {library.media_items_count}")
        print(f"Total playlists: {library.playlists_count}")

        # Show first few media items
        print("\nFirst 5 media items:")
        for i in range(min(5, library.media_items_count)):
            item = library.get_media_item(i)
            print(f"  {i + 1}. {item.title} by {item.artist} ({item.duration}s)")

        # Show first few playlists
        print("\nFirst 5 playlists:")
        for i in range(min(5, library.playlists_count)):
            playlist = library.get_playlist(i)
            print(f"  {i + 1}. {playlist.name} ({playlist.item_count} items)")

        print("\nExample completed successfully!")

    except ITLibraryError as e:
        print(f"iTunes Library Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def export_library_to_csv(
    filepath: str, audio_only: bool = True, limit: Optional[int] = None
) -> None:
    """Convenience function to export iTunes Library to CSV for media migration.

    Args:
        filepath: Path to save the CSV file
        audio_only: If True, filter out video content (default: True)
        limit: Optional limit on number of items to export
    """
    from .helpers import LibraryBenchmark

    benchmark = LibraryBenchmark()
    benchmark.save_library_export(
        filepath, format="csv", audio_only=audio_only, limit=limit
    )


def export_library_to_dataframe(audio_only: bool = True, limit: Optional[int] = None):
    """Convenience function to export iTunes Library to pandas DataFrame.

    Args:
        audio_only: If True, filter out video content (default: True)
        limit: Optional limit on number of items to export

    Returns:
        pandas.DataFrame with comprehensive track metadata
    """
    from .helpers import LibraryBenchmark

    benchmark = LibraryBenchmark()
    return benchmark.export_library_to_dataframe(audio_only=audio_only, limit=limit)
