import os
import uuid
from .database import db
from .models import (
    User,
    Album,
    Song,
    Playlist,
    PlaylistSong,
    Rating,
    Flag,
)
from datetime import time


def generate_filename(filename):
    ext = os.path.splitext(filename)[1]
    unique_filename = str(uuid.uuid4()) + ext
    return unique_filename


def create_dummy_data(app):
    with app.app_context():
        # Create dummy users
        user1 = User(
            username="john_doe",
            email="john@example.com",
            password="password",
            role="admin",
            gender="M",
            mobile_number="911234567890",
            image_path="/Users/vagadeeshwar/Desktop/MAD_Files/Image_Files/ben-sweet-2LowviVHZ-E-unsplash",
        )
        user2 = User(
            username="jane_smith",
            email="jane@example.com",
            password="password",
            role="user",
            gender="F",
            mobile_number="919876543210",
            image_path="/Users/vagadeeshwar/Desktop/MAD_Files/Image_Files/christopher-campbell-rDEOVtE7vOs-unsplash",
        )
        db.session.add_all([user1, user2])
        db.session.commit()

        # Create dummy albums
        album1 = Album(
            name="Album 1",
            user_id=user1.id,
            description="Dummy album 1",
            genre="Rock",
        )
        album2 = Album(
            name="Album 2",
            user_id=user2.id,
            description="Dummy album 2",
            genre="Pop",
        )
        db.session.add_all([album1, album2])
        db.session.commit()

        # Create dummy songs
        song1 = Song(
            name="Song 1",
            album_id=album1.id,
            lyrics="Lyrics of song 1",
            genre="Rock",
            duration=time(*(int(x) for x in "00:03:30".split(":"))),
            audio_path="/Users/vagadeeshwar/Desktop/MAD_Files/Audio_Files/file_example_MP3_700KB",
        )
        song2 = Song(
            name="Song 2",
            album_id=album1.id,
            lyrics="Lyrics of song 2",
            genre="Rock",
            duration=time(*(int(x) for x in "00:03:45".split(":"))),
            audio_path="/Users/vagadeeshwar/Desktop/MAD_Files/Audio_Files/sample-6s",
        )
        song3 = Song(
            name="Song 3",
            album_id=album2.id,
            lyrics="Lyrics of song 3",
            genre="Pop",
            duration=time(*(int(x) for x in "00:01:15".split(":"))),
            audio_path="/Users/vagadeeshwar/Desktop/MAD_Files/Audio_Files/sample-9s",
        )
        db.session.add_all([song1, song2, song3])
        db.session.commit()

        # Create dummy playlists
        playlist1 = Playlist(
            name="Playlist 1", user_id=user1.id, description="Dummy playlist 1"
        )
        playlist2 = Playlist(
            name="Playlist 2", user_id=user2.id, description="Dummy playlist 2"
        )
        db.session.add_all([playlist1, playlist2])
        db.session.commit()

        # Create dummy playlist songs
        playlist_song1 = PlaylistSong(playlist_id=playlist1.id, song_id=song1.id)
        playlist_song2 = PlaylistSong(playlist_id=playlist1.id, song_id=song2.id)
        playlist_song3 = PlaylistSong(playlist_id=playlist2.id, song_id=song3.id)
        db.session.add_all([playlist_song1, playlist_song2, playlist_song3])
        db.session.commit()

        # Create dummy ratings
        rating1 = Rating(user_id=user1.id, song_id=song1.id, rating_value=4)
        rating2 = Rating(user_id=user2.id, song_id=song2.id, rating_value=5)
        db.session.add_all([rating1, rating2])
        db.session.commit()

        # Create dummy flags
        flag1 = Flag(user_id=user1.id, song_id=song3.id, reason="Good lyrics")
        db.session.add(flag1)
        db.session.commit()
