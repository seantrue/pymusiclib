#!/usr/bin/env python3
"""
Test iTunes Library authorization
"""

import sys


def main():
    try:
        import itlibrary

        print("iTunes Library Authorization Test")
        print("=" * 50)

        print("1. Attempting to initialize iTunes Library...")

        try:
            library = itlibrary.ITLibrary()
            print("✓ SUCCESS: iTunes Library initialized!")

            print(f"   Media items: {library.media_items_count}")
            print(f"   Playlists: {library.playlists_count}")
            print(f"   Media folder: {library.media_folder_location}")

            if library.media_items_count > 0:
                print("\n2. Testing media item access...")
                item = library.get_media_item(0)
                print(f"   First track: {item.title} by {item.artist}")

            print("\n✓ All tests passed! iTunes Library access is working.")
            return True

        except itlibrary.ITLibraryError as e:
            print(f"✗ FAILED: {e}")
            print("\nTroubleshooting steps:")
            print("1. Open Music app and make sure it has some content")
            print("2. Go to System Settings → Privacy & Security → Media & Apple Music")
            print("3. Add Terminal (or Python) to allowed applications")
            print("4. Try running as admin: sudo python test_auth.py")
            print("5. Restart Terminal after changing permissions")
            return False

    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Run: make build && make install-dev")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
