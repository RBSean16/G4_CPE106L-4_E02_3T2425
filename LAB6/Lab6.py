from pymongo import MongoClient

# Connect to local MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["chinook"]

# Get references to the collections
artists_collection = db["artists"]
albums_collection = db["albums"]
tracks_collection = db["tracks"]

# --- Fetch all artists and their related albums/tracks ---
print("--- All Artists, Albums, and Tracks (Hierarchical View) ---")
if artists_collection.count_documents({}) > 0:
    for artist in artists_collection.find():
        artist_name = artist.get('Name', 'N/A')
        artist_id = artist.get('ArtistId', 'N/A')
        print(f"\nArtist: {artist_name} (ArtistId: {artist_id})")

        # Fetch albums for this artist by matching ArtistId
        artist_albums = albums_collection.find({"ArtistId": artist_id})
        for album in artist_albums:
            album_title = album.get('Title', 'N/A')
            album_id = album.get('AlbumId', 'N/A')
            print(f"  Album: {album_title} (AlbumId: {album_id})")

            # Fetch tracks for this album by matching AlbumId
            album_tracks = tracks_collection.find({"AlbumId": album_id})
            for track in album_tracks:
                track_name = track.get('Name', 'N/A')
                track_id = track.get('TrackId', 'N/A')
                print(f"    Track: {track_name} (TrackId: {track_id})")
else:
    print("No documents found in 'artists' collection. Please ensure data is imported correctly.")

# Close the connection
client.close()
print("\n--- Connection Closed ---")
