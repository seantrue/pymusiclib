# ITLibrary Bridge Makefile
# Build system for Python iTunes Library bindings

.PHONY: all build build-universal clean install test benchmark help

# Default target
all: check format lint typecheck install-dev test-cov

# Variables
SWIFT_FILE = SwiftITLibBridge.swift
LIB_NAME = libitlibrary.dylib
SRC_PATH=src
PACKAGE_PREFIX ?= $(SRC_PATH)/musiclib
LIB_PATH=$(PACKAGE_PREFIX)/$(LIB_NAME)
LIB_PATH_ARM64=$(PACKAGE_PREFIX)/$(LIB_NAME).arm64
LIB_PATH_X86_64=$(PACKAGE_PREFIX)/$(LIB_NAME).x86_64
PYTHON ?= python

# Check prerequisites
check:
	@echo "Checking prerequisites..."
	@command -v swift >/dev/null 2>&1 || { echo "Swift compiler not found. Please install Xcode or Swift toolchain."; exit 1; }
	@command -v $(PYTHON) >/dev/null 2>&1 || { echo "Python not found at $(PYTHON)"; exit 1; }
	@$(PYTHON) -c "import numpy" 2>/dev/null || { echo "NumPy not installed. Run: pip install numpy"; exit 1; }
	@echo "All prerequisites satisfied!"

# Format Python code
format:
	@echo "Formatting Python code..."
	uv run black $(PACKAGE_PREFIX)/*.py $(PACKAGE_PREFIX)/scripts/*.py tests/*.py examples/*.py --line-length 88
	@echo "Formatting complete!"

# Lint Python code
lint:
	@echo "Linting Python code..."
	uv run ruff check $(PACKAGE_PREFIX)/ tests/ examples/
	@echo "Linting complete!"

# Fix lint issues automatically
lint-fix:
	@echo "Fixing lint issues..."
	uv run ruff check --fix $(PACKAGE_PREFIX)/ tests/ examples/
	@echo "Lint fixes applied!"

# Make sure required packages are license compatible
licensecheck:
	@echo "Checking packages for compatibility..."
	uv run licensecheck
	@echo "License check complete"

# Type checking
typecheck:
	@echo "Running type checks..."
	uv run mypy src/musiclib tests --ignore-missing-imports
	@echo "Type checking complete!"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -f $(LIB_PATH)
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	find . -name "*.pyc" -delete -print
	find . -name "*.pyo" -delete -print
	find src -name "*.dylib" -delete -print
	find src -name "*.gif" -delete -print
	@echo "Clean complete!"

$(LIB_PATH): $(SRC_PATH)/$(SWIFT_FILE)
	@echo "Compiling Swift Metal bridge..."
	swiftc -emit-library -o $(LIB_PATH) \
		-Xlinker -install_name -Xlinker @rpath/$(LIB_NAME) \
		-framework iTunesLibrary \
		$(SRC_PATH)/$(SWIFT_FILE)
	@echo "Successfully built $(LIB_PATH)"

# Build the Swift bridge library
build: $(LIB_PATH)
	@echo "Build complete!"

# Build ARM64 version
$(LIB_PATH_ARM64): $(SRC_PATH)/$(SWIFT_FILE)
	@echo "Compiling Swift iTunes Library bridge for ARM64..."
	swiftc -emit-library -o $(LIB_PATH_ARM64) \
		-target arm64-apple-macos10.10 \
		-Xlinker -install_name -Xlinker @rpath/$(LIB_NAME) \
		-framework iTunesLibrary \
		$(SRC_PATH)/$(SWIFT_FILE)
	@echo "Successfully built ARM64 version: $(LIB_PATH_ARM64)"

# Build x86_64 version
$(LIB_PATH_X86_64): $(SRC_PATH)/$(SWIFT_FILE)
	@echo "Compiling Swift iTunes Library bridge for x86_64..."
	swiftc -emit-library -o $(LIB_PATH_X86_64) \
		-target x86_64-apple-macos10.10 \
		-Xlinker -install_name -Xlinker @rpath/$(LIB_NAME) \
		-framework iTunesLibrary \
		$(SRC_PATH)/$(SWIFT_FILE)
	@echo "Successfully built x86_64 version: $(LIB_PATH_X86_64)"

# Build universal binary
build-universal: $(LIB_PATH_ARM64) $(LIB_PATH_X86_64)
	@echo "Creating universal binary..."
	lipo -create -output $(LIB_PATH) $(LIB_PATH_ARM64) $(LIB_PATH_X86_64)
	@echo "Successfully created universal binary: $(LIB_PATH)"
	@lipo -info $(LIB_PATH)
	@echo "Cleaning up architecture-specific files..."
	rm -f $(LIB_PATH_ARM64) $(LIB_PATH_X86_64)
	@echo "Universal build complete!"

# Create distribution package
dist: clean build
	@echo "Creating distribution package..."
	uv build
	@echo "Distribution package created in dist/"

# Install the library
install: dist
	@echo "Installing Python package..."
	uv pip install dist/pymetallic*.whl
	@echo "Installation complete!"

# Install for development (current user only)
install-dev: uninstall
	@echo "Installing for development..."
	uv sync --dev
	@echo "Development installation complete!"

# Run smoke test
smoke: $(LIB_PATH)
	@echo "Running smoke tests..."
	uv run python -c "import musiclib; musiclib.run_simple_library_example()"
	uv run python src/musiclib/scripts/smoke.py
	@echo "Smoke tests passed!"

# Run test suite
test: $(LIB_PATH)
	@echo "Running tests..."
	uv run pytest tests/
	@echo "Tests complete!"

# Run test suite with coverage
test-cov: $(LIB_PATH)
	@echo "Running tests with coverage..."
	uv run pytest --cov=src/pymetallic --cov-report=html:coverage tests/
	@echo "Tests complete! Coverage report at coverage/index.html"


# Run performance benchmarks
benchmark: $(LIB_PATH)
	@echo "Running performance benchmarks..."
	$(PYTHON) -c "from musiclib.helpers import LibraryBenchmark; b = LibraryBenchmark(); b.benchmark_library_access()"

# Run comprehensive examples
demos: $(LIB_PATH)
	@echo "Running all demos..."
	$(PYTHON) src/musiclib/scripts/demo.py --demos all

# Export library data
export-stats:
	@echo "Showing library statistics..."
	$(PYTHON) src/musiclib/scripts/export.py --stats

export-sample:
	@echo "Exporting sample library data..."
	$(PYTHON) src/musiclib/scripts/export.py claude-debug/library_sample.csv --limit 50

# Run basic examples
examples: $(LIB_PATH)
	@echo "Running examples..."
	$(PYTHON) examples/basic_compute.py
	@echo "Examples complete!"

uninstall:
	@echo "Uninstalling Python package..."
	uv pip uninstall musiclib
	@echo "Uninstallation complete..."


# Help target
help:
	@echo "ITLibrary Bridge Build System"
	@echo "==================="
	@echo ""
	@echo "Available targets:"
	@echo "  check        - Check prerequisites"
	@echo "  format       - Format Python code with black"
	@echo "  typecheck    - Run type checking with mypy"
	@echo "  licensecheck - Check required package licenses"
	@echo "  clean        - Remove build artifacts"
	@echo "  build        - Build the Swift bridge library (current architecture)"
	@echo "  build-universal - Build universal binary (ARM64 + x86_64)"
	@echo "  dist         - Create distribution package"
	@echo "  uninstall    - Uninstall package from site_packages"
	@echo "  install      - Install Python package from wheel to site_packages"
	@echo "  install-dev  - Install for development (user-only)"
	@echo "  smoke        - Run basic functional test"
	@echo "  test         - Run all tests"
	@echo "  test-cov     - Run all tests with coverage"
	@echo "  examples     - Run comprehensive examples"
	@echo "  benchmark    - Run performance benchmarks"
	@echo "  export-stats - Show library statistics for export planning"
	@echo "  export-sample- Export sample library data to CSV"
	@echo "  help         - Show this help message"
	@echo ""
	@echo "Variables:"
	@echo "  PACKAGE_PREFIX - Path to src directory (default: $(PACKAGE_PREFIX))"
	@echo "  PYTHON         - Python executable (default: python3) if we're on macOS"
UNAME_S := $(shell uname -s)
ifneq ($(UNAME_S),Darwin)
$(error ITLibrary Bridge requires macOS with iTunes Library framework support)
endif