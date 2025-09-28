# PyMusicLib

Python bindings for Apple's iTunes Library (ITlib) API, enabling programmatic access to iTunes/Music library data on macOS with powerful export and organization tools.

## Overview

PyMusicLib provides a comprehensive Python interface to access iTunes/Music library information with advanced data export and music organization capabilities:

### Core Library Access
- Media items (songs, tracks) with comprehensive metadata (title, artist, album, duration, bitrate, ratings, etc.)
- Playlists and their contents
- Library folder locations and file paths
- Search functionality by title and artist
- Performance benchmarking tools

### Data Export & Analysis
- **CSV Export**: Export library data with extensive filtering and search options
- **Excel Export**: Rich formatted exports with multiple worksheet support
- **JSON/Parquet**: Support for modern data formats
- **Advanced Filtering**: Filter by genre, year, bitrate, rating, date added, and more
- **Search Capabilities**: Full-text search across titles, artists, and albums
- **Performance Analysis**: Built-in library statistics and benchmarking

### Music Organization Tools
- **Servify**: Organize music files into Plex-compatible directory structures
- **Flexible naming patterns**: Customizable track and folder naming
- **Dry-run mode**: Preview organization before making changes
- **Batch processing**: Handle large libraries efficiently

## Requirements

- **macOS 10.7+** with iTunes Library framework
- **Swift toolchain** for compilation
- **Python 3.10+**
- **Required packages**: NumPy, Pandas, OpenPyXL
- **Optional**: Pillow (for image processing features)

## Installation

### Development Setup

```bash
# Clone the repository
git clone https://github.com/seantrue/pymusiclib.git
cd pymusiclib

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

# Show library statistics
make export-stats
```

## Usage

### Basic Library Access

```python
import pymusiclib

# Initialize library connection
library = pymusiclib.ITLibrary()

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

### Advanced Data Export

```python
from pymusiclib.helpers import LibraryBenchmark

# Export library to CSV with filtering
benchmark = LibraryBenchmark()
df = benchmark.export_library_to_dataframe(
    audio_only=True,
    limit=1000
)

# Save to various formats
df.to_csv("my_library.csv", index=False)
df.to_excel("my_library.xlsx", index=False)
```

### Command-Line Tools

#### Library Export Tool

```bash
# Export entire library to CSV
pymusiclib-export library.csv

# Export with advanced filtering
pymusiclib-export filtered.csv --genre-filter rock --year-min 1990 --year-max 2000

# Export high-quality tracks to Excel
pymusiclib-export hq_music.xlsx --format excel --bitrate-min 256

# Show library statistics for planning
pymusiclib-export --stats

# Search and export specific content
pymusiclib-export beatles.csv --artist-search "beatles"
```

#### Music Organization Tool

```bash
# Organize music files from exported CSV
python utils/servify.py library.csv

# Preview organization without copying files
python utils/servify.py library.csv --dry-run

# Custom output directory and track naming
python utils/servify.py library.csv --output /media/music --track-format "{track:03d}. {title}"

# Force overwrite existing files
python utils/servify.py library.csv --force

# Quiet mode for scripting
python utils/servify.py library.csv --quiet
```

#### Demo and Testing

```bash
# Run smoke tests
pymusiclib-smoke

# Run comprehensive demos
pymusiclib-demo

# Run specific demo types
pymusiclib-demo --demos basic
pymusiclib-demo --demos benchmarks
```

## Architecture

PyMusicLib uses a hybrid Python/Swift architecture:

1. **Python Layer** (`src/pymusiclib/`) - Main API, export tools, and data processing
2. **Swift Bridge** (`src/SwiftITLibBridge.swift`) - Native iTunes Library interface
3. **Dynamic Library** (`libitlibrary.dylib`) - Compiled Swift bridge
4. **Command-Line Tools** - Export, organization, and testing utilities

The flow is: Python → ctypes → Swift dylib → iTunes Library Framework

### Key Components

- **`pymusiclib.py`** - Core iTunes Library API classes
- **`helpers.py`** - Data export, benchmarking, and analysis tools
- **`scripts/export.py`** - Advanced command-line export tool
- **`utils/servify.py`** - Music file organization utility
- **`scripts/demo.py`** - Comprehensive demonstration suite
- **`scripts/smoke.py`** - Quick validation tests

## Development

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Type checking
make typecheck

# Run tests (skip slow benchmarks)
uv run pytest -m "not slow"

# Run all tests including performance benchmarks
make test
```

### Export and Analysis

```bash
# Export sample library data
make export-sample

# Show library statistics
make export-stats

# Run performance benchmarks
make benchmark
```

### Building and Distribution

```bash
# Clean build artifacts
make clean

# Build universal binary (ARM64 + x86_64)
make build-universal

# Create distribution package
make dist

# Install from wheel
make install
```

## Features

### Data Export Capabilities

- **Comprehensive Metadata**: Extract all available iTunes metadata fields
- **Advanced Filtering**: Multiple filter types including ranges, text search, and date filtering
- **Multiple Formats**: CSV, Excel, JSON, and Parquet export support
- **Performance Optimized**: Efficient processing of large libraries
- **Progress Reporting**: Real-time statistics and progress updates

### Music Organization

- **Plex-Compatible Structure**: Organize files as Artist/Album/Track format
- **Flexible Naming**: Customizable track and folder naming patterns
- **Safe Operations**: Dry-run mode and file validation
- **Cross-Platform Paths**: Automatic filename sanitization
- **Batch Processing**: Handle thousands of files efficiently

### Analysis Tools

- **Library Statistics**: Comprehensive analysis of your music collection
- **Performance Benchmarks**: Measure library access and processing speeds
- **Search Analytics**: Analyze search performance and results
- **Data Quality**: Identify missing metadata and file issues

## Important Notes

- **macOS Only**: This library only works on macOS with the iTunes Library framework
- **Permissions**: May require user permission for iTunes/Music library access on first run
- **Swift Compilation**: The Swift bridge must be compiled before Python code can run (`make build`)
- **Library Content**: Many features depend on having media content in your iTunes/Music library
- **File Access**: Export and organization features require accessible file paths

## CLI Commands

After installation, the following commands are available:

- **`pymusiclib-export`** - Advanced data export with filtering and search
- **`pymusiclib-demo`** - Comprehensive demonstration of library capabilities
- **`pymusiclib-smoke`** - Quick validation and testing
- **`utils/servify.py`** - Music file organization utility

## Examples

### Export Recent High-Quality Music

```bash
# Export tracks added in 2024 with high bitrate
pymusiclib-export recent_hq.csv \
  --date-added-after 2024-01-01 \
  --bitrate-min 256 \
  --format csv
```

### Organize Music Library for Plex

```bash
# Export library data
pymusiclib-export my_library.csv

# Organize files with custom naming
python utils/servify.py my_library.csv \
  --output /media/plex-music \
  --track-format "{track:02d} - {title}" \
  --dry-run
```

### Library Analysis

```bash
# Show comprehensive library statistics
pymusiclib-export --stats

# Export analysis data for external tools
pymusiclib-export analysis.xlsx \
  --format excel \
  --include-unrated \
  --local-only
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Submit a pull request

For development setup and contribution guidelines, see [CLAUDE.md](CLAUDE.md).