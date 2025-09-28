# ITLibrary Bridge

Python bindings for Apple's iTunes Library (ITlib) API, enabling programmatic access to iTunes/Music library data on macOS.

## Overview

ITLibrary Bridge provides a Python interface to access iTunes/Music library information including:

- Media items (songs, tracks) with metadata (title, artist, album, duration, etc.)
- Playlists and their contents
- Library folder locations
- Search functionality by title and artist

## Requirements

- **macOS 10.7+** with iTunes Library framework
- **Swift toolchain** for compilation
- **Python 3.10+**
- **NumPy**

## Installation

### Development Setup

```bash
# Clone the repository
git clone https://github.com/seantrue/itlibrary-bridge.git
cd itlibrary-bridge

# Check prerequisites
make check

# Build the Swift bridge
make build

# Install for development
make install-dev
```

### Quick Test

```bash
# Run smoke tests
make smoke

# Run comprehensive demo
make demos
```

## Usage

```python
import itlibrary

# Initialize library connection
library = itlibrary.ITLibrary()

# Get library info
print(f"Media items: {library.media_items_count}")
print(f"Playlists: {library.playlists_count}")
print(f"Music folder: {library.music_folder_location}")

# Access media items
item = library.get_media_item(0)
print(f"Title: {item.title}")
print(f"Artist: {item.artist}")
print(f"Album: {item.album}")
print(f"Duration: {item.duration} seconds")

# Search functionality
matches = library.search_by_title("love")
print(f"Found {matches} songs with 'love' in title")
```

## Architecture

ITLibrary Bridge uses a hybrid Python/Swift architecture:

1. **Python Layer** (`src/itlibrary/`) - Main API and ctypes bindings
2. **Swift Bridge** (`src/SwiftITLibBridge.swift`) - Native iTunes Library interface
3. **Dynamic Library** (`libitlibrary.dylib`) - Compiled Swift bridge

The flow is: Python → ctypes → Swift dylib → iTunes Library Framework

## Development

```bash
# Format code
make format

# Run linting
make lint

# Type checking
make typecheck

# Run tests
make test

# Performance benchmarks
make benchmark
```

## Important Notes

- **macOS Only**: This library only works on macOS with the iTunes Library framework
- **Permissions**: May require user permission for iTunes/Music library access on first run
- **Swift Compilation**: The Swift bridge must be compiled before Python code can run

## License

MIT License - see LICENSE file for details.