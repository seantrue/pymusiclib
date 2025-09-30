#!/usr/bin/env python3
"""
MusicLib: Python bindings for iTunes Library (ITlib) API using Swift bridge
Access iTunes/Music library data programmatically on macOS
"""

# Public API exports
from .musiclib import (
    ITLibrary,
    ITLibraryError,
    MediaItem,
    Playlist,
    run_simple_library_example,
    export_library_to_csv,
    export_library_to_dataframe,
)

__all__ = [
    "ITLibraryError",
    "ITLibrary",
    "MediaItem",
    "Playlist",
    "run_simple_library_example",
    "export_library_to_csv",
    "export_library_to_dataframe",
]

__version__ = "0.1.0"

if __name__ == "__main__":
    print("MusicLib: Python bindings for iTunes Library")
    print(
        "Note: This requires the Swift bridge library (libitlibrary.dylib) to be compiled and available"
    )
    # Uncomment to run example (requires compiled bridge library)
    run_simple_library_example()
