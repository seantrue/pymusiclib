import Foundation
import iTunesLibrary

// MARK: - String Helper

private func createCString(from string: String?) -> UnsafeMutablePointer<CChar>? {
    guard let string = string else { return nil }
    return strdup(string)
}

// MARK: - Error Handling

private var lastError: String? = nil

@_cdecl("itlib_get_last_error")
public func itlib_get_last_error() -> UnsafeMutablePointer<CChar>? {
    guard let error = lastError else { return nil }
    return createCString(from: error)
}

private func setError(_ message: String) {
    lastError = message
    print("ITLib Error: \(message)")
}

private func clearError() {
    lastError = nil
}

// MARK: - Library Management

private var globalLibrary: ITLibrary? = nil

@_cdecl("itlib_initialize")
public func itlib_initialize() -> Bool {
    clearError()

    do {
        globalLibrary = try ITLibrary(apiVersion: "1.0")
        return true
    } catch {
        setError("Failed to initialize iTunes Library: \(error.localizedDescription)")
        return false
    }
}

@_cdecl("itlib_cleanup")
public func itlib_cleanup() {
    globalLibrary = nil
    clearError()
}

@_cdecl("itlib_is_initialized")
public func itlib_is_initialized() -> Bool {
    return globalLibrary != nil
}

// MARK: - Library Information

@_cdecl("itlib_get_media_folder_location")
public func itlib_get_media_folder_location() -> UnsafeMutablePointer<CChar>? {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return nil
    }

    guard let location = library.mediaFolderLocation else {
        setError("Media folder location not available")
        return nil
    }

    return createCString(from: location.path)
}

@_cdecl("itlib_get_music_folder_location")
public func itlib_get_music_folder_location() -> UnsafeMutablePointer<CChar>? {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return nil
    }

    guard let location = library.musicFolderLocation else {
        setError("Music folder location not available")
        return nil
    }

    return createCString(from: location.path)
}

// MARK: - Media Items

@_cdecl("itlib_get_media_items_count")
public func itlib_get_media_items_count() -> Int32 {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return -1
    }

    return Int32(library.allMediaItems.count)
}

@_cdecl("itlib_get_media_item_title")
public func itlib_get_media_item_title(_ index: Int32) -> UnsafeMutablePointer<CChar>? {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return nil
    }

    let items = library.allMediaItems
    guard index >= 0 && index < items.count else {
        setError("Media item index out of range")
        return nil
    }

    let item = items[Int(index)]
    return createCString(from: item.title)
}

@_cdecl("itlib_get_media_item_artist")
public func itlib_get_media_item_artist(_ index: Int32) -> UnsafeMutablePointer<CChar>? {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return nil
    }

    let items = library.allMediaItems
    guard index >= 0 && index < items.count else {
        setError("Media item index out of range")
        return nil
    }

    let item = items[Int(index)]
    return createCString(from: item.artist?.name)
}

@_cdecl("itlib_get_media_item_album")
public func itlib_get_media_item_album(_ index: Int32) -> UnsafeMutablePointer<CChar>? {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return nil
    }

    let items = library.allMediaItems
    guard index >= 0 && index < items.count else {
        setError("Media item index out of range")
        return nil
    }

    let item = items[Int(index)]
    return createCString(from: item.album.title)
}

@_cdecl("itlib_get_media_item_duration")
public func itlib_get_media_item_duration(_ index: Int32) -> Int32 {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return -1
    }

    let items = library.allMediaItems
    guard index >= 0 && index < items.count else {
        setError("Media item index out of range")
        return -1
    }

    let item = items[Int(index)]
    return Int32(item.totalTime / 1000) // Convert milliseconds to seconds
}

@_cdecl("itlib_get_media_item_track_number")
public func itlib_get_media_item_track_number(_ index: Int32) -> Int32 {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return -1
    }

    let items = library.allMediaItems
    guard index >= 0 && index < items.count else {
        setError("Media item index out of range")
        return -1
    }

    let item = items[Int(index)]
    return Int32(item.trackNumber)
}

@_cdecl("itlib_get_media_item_year")
public func itlib_get_media_item_year(_ index: Int32) -> Int32 {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return -1
    }

    let items = library.allMediaItems
    guard index >= 0 && index < items.count else {
        setError("Media item index out of range")
        return -1
    }

    let item = items[Int(index)]
    return Int32(item.year)
}

@_cdecl("itlib_get_media_item_location")
public func itlib_get_media_item_location(_ index: Int32) -> UnsafeMutablePointer<CChar>? {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return nil
    }

    let items = library.allMediaItems
    guard index >= 0 && index < items.count else {
        setError("Media item index out of range")
        return nil
    }

    let item = items[Int(index)]
    return createCString(from: item.location?.path)
}

@_cdecl("itlib_get_media_item_genre")
public func itlib_get_media_item_genre(_ index: Int32) -> UnsafeMutablePointer<CChar>? {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return nil
    }

    let items = library.allMediaItems
    guard index >= 0 && index < items.count else {
        setError("Media item index out of range")
        return nil
    }

    let item = items[Int(index)]
    return createCString(from: item.genre)
}

@_cdecl("itlib_get_media_item_bitrate")
public func itlib_get_media_item_bitrate(_ index: Int32) -> Int64 {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return -1
    }

    let items = library.allMediaItems
    guard index >= 0 && index < items.count else {
        setError("Media item index out of range")
        return -1
    }

    let item = items[Int(index)]
    return Int64(item.bitrate)
}

@_cdecl("itlib_get_media_item_sample_rate")
public func itlib_get_media_item_sample_rate(_ index: Int32) -> Int64 {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return -1
    }

    let items = library.allMediaItems
    guard index >= 0 && index < items.count else {
        setError("Media item index out of range")
        return -1
    }

    let item = items[Int(index)]
    return Int64(item.sampleRate)
}

@_cdecl("itlib_get_media_item_file_size")
public func itlib_get_media_item_file_size(_ index: Int32) -> Int64 {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return -1
    }

    let items = library.allMediaItems
    guard index >= 0 && index < items.count else {
        setError("Media item index out of range")
        return -1
    }

    let item = items[Int(index)]
    return Int64(item.fileSize)
}

@_cdecl("itlib_get_media_item_kind")
public func itlib_get_media_item_kind(_ index: Int32) -> UnsafeMutablePointer<CChar>? {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return nil
    }

    let items = library.allMediaItems
    guard index >= 0 && index < items.count else {
        setError("Media item index out of range")
        return nil
    }

    let item = items[Int(index)]
    return createCString(from: item.kind)
}

@_cdecl("itlib_get_media_item_album_artist")
public func itlib_get_media_item_album_artist(_ index: Int32) -> UnsafeMutablePointer<CChar>? {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return nil
    }

    let items = library.allMediaItems
    guard index >= 0 && index < items.count else {
        setError("Media item index out of range")
        return nil
    }

    let item = items[Int(index)]
    return createCString(from: item.album.albumArtist)
}

@_cdecl("itlib_get_media_item_total_time_ms")
public func itlib_get_media_item_total_time_ms(_ index: Int32) -> Int64 {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return -1
    }

    let items = library.allMediaItems
    guard index >= 0 && index < items.count else {
        setError("Media item index out of range")
        return -1
    }

    let item = items[Int(index)]
    return Int64(item.totalTime)
}

@_cdecl("itlib_get_media_item_play_count")
public func itlib_get_media_item_play_count(_ index: Int32) -> Int32 {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return -1
    }

    let items = library.allMediaItems
    guard index >= 0 && index < items.count else {
        setError("Media item index out of range")
        return -1
    }

    let item = items[Int(index)]
    return Int32(item.playCount)
}

@_cdecl("itlib_get_media_item_rating")
public func itlib_get_media_item_rating(_ index: Int32) -> Int32 {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return -1
    }

    let items = library.allMediaItems
    guard index >= 0 && index < items.count else {
        setError("Media item index out of range")
        return -1
    }

    let item = items[Int(index)]
    return Int32(item.rating)
}

@_cdecl("itlib_get_media_item_is_video")
public func itlib_get_media_item_is_video(_ index: Int32) -> Bool {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return false
    }

    let items = library.allMediaItems
    guard index >= 0 && index < items.count else {
        setError("Media item index out of range")
        return false
    }

    let item = items[Int(index)]
    return item.isVideo
}

@_cdecl("itlib_get_media_item_date_added")
public func itlib_get_media_item_date_added(_ index: Int32) -> Int64 {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return -1
    }

    let items = library.allMediaItems
    guard index >= 0 && index < items.count else {
        setError("Media item index out of range")
        return -1
    }

    let item = items[Int(index)]
    guard let addedDate = item.addedDate else {
        return 0  // Return 0 if no date available
    }

    // Return Unix timestamp (seconds since Jan 1, 1970)
    return Int64(addedDate.timeIntervalSince1970)
}

// MARK: - Playlists

@_cdecl("itlib_get_playlists_count")
public func itlib_get_playlists_count() -> Int32 {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return -1
    }

    return Int32(library.allPlaylists.count)
}

@_cdecl("itlib_get_playlist_name")
public func itlib_get_playlist_name(_ index: Int32) -> UnsafeMutablePointer<CChar>? {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return nil
    }

    let playlists = library.allPlaylists
    guard index >= 0 && index < playlists.count else {
        setError("Playlist index out of range")
        return nil
    }

    let playlist = playlists[Int(index)]
    return createCString(from: playlist.name)
}

@_cdecl("itlib_get_playlist_items_count")
public func itlib_get_playlist_items_count(_ index: Int32) -> Int32 {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return -1
    }

    let playlists = library.allPlaylists
    guard index >= 0 && index < playlists.count else {
        setError("Playlist index out of range")
        return -1
    }

    let playlist = playlists[Int(index)]
    return Int32(playlist.items.count)
}

// MARK: - Search Functions

@_cdecl("itlib_search_media_items_by_title")
public func itlib_search_media_items_by_title(_ searchTerm: UnsafePointer<CChar>) -> Int32 {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return -1
    }

    let search = String(cString: searchTerm).lowercased()
    let items = library.allMediaItems
    let matchingItems = items.filter { item in
        let title = item.title
        return title.lowercased().contains(search)
    }

    return Int32(matchingItems.count)
}

@_cdecl("itlib_search_media_items_by_artist")
public func itlib_search_media_items_by_artist(_ searchTerm: UnsafePointer<CChar>) -> Int32 {
    guard let library = globalLibrary else {
        setError("Library not initialized")
        return -1
    }

    let search = String(cString: searchTerm).lowercased()
    let items = library.allMediaItems
    let matchingItems = items.filter { item in
        guard let artistName = item.artist?.name else { return false }
        return artistName.lowercased().contains(search)
    }

    return Int32(matchingItems.count)
}