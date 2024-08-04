from application.database import db
from datetime import datetime, timezone, date


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    gender = db.Column(db.String(1), nullable=False)
    dob = db.Column(db.Time, nullable=True)
    mobile_number = db.Column(db.String(12), nullable=False, unique=True)
    image_path = db.Column(db.String(255), nullable=True)

    albums = db.relationship("Album", backref="user", lazy=True)
    playlists = db.relationship("Playlist", backref="user", lazy=True)
    ratings = db.relationship("Rating", backref="user", lazy=True)
    flags = db.relationship("Flag", backref="user", lazy=True)

    __table_args__ = (
        db.CheckConstraint(db.func.length(username) >= 2, name="username_length_check"),
        db.CheckConstraint(db.column("email").like("%@%.%"), name="email_format_check"),
        db.CheckConstraint(role.in_(["user", "admin", "creator"]), name="role_check"),
        db.CheckConstraint(
            gender.in_(["M", "F"]), name="gender_check"
        ),  # this is the best sqlite db can do... sqlite db does not support regex unlike mysql or postgre
        db.CheckConstraint(
            db.column("mobile_number").like("____________")
            & (db.column("mobile_number") != "000000000000"),
            name="mobile_number_format_check",
        ),
        db.CheckConstraint(db.column("dob") <= date.today(), name="dob_not_future"),
    )

    def __repr__(self):
        return f"<User {self.username}>"


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    album_id = db.Column(db.Integer, db.ForeignKey("album.id"), nullable=False)
    lyrics = db.Column(db.Text, nullable=True)
    genre = db.Column(db.String(80), nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now(timezone.utc)
    )
    duration = db.Column(db.Time, nullable=False)
    audio_path = db.Column(db.String(255), nullable=False)

    ratings = db.relationship("Rating", backref="song", lazy=True)
    flags = db.relationship("Flag", backref="song", lazy=True)

    __table_args__ = (
        db.CheckConstraint(db.func.length(name) >= 2, name="song_name_length_check"),
        db.CheckConstraint(
            genre.is_(None) | (db.func.length(genre) >= 2), name="genre_length_check"
        ),
        db.CheckConstraint(duration >= 1, name="duration_check"),
        db.CheckConstraint(
            audio_path.isnot(None) & (db.func.length(audio_path) > 0),
            name="audio_path_check",
        ),
        db.CheckConstraint(
            db.column("created_at") <= datetime.now(timezone.utc),
            name="album_created_at_not_future",
        ),
    )

    def __repr__(self):
        return f"<Song {self.name}>"


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now(timezone.utc)
    )
    description = db.Column(db.String(200), nullable=True)
    genre = db.Column(db.String(80), nullable=True)
    songs = db.relationship("Song", backref="album", lazy=True)

    __table_args__ = (
        db.CheckConstraint(db.func.length(name) >= 2, name="album_name_length_check"),
        db.CheckConstraint(
            genre.is_(None) | (db.func.length(genre) >= 2),
            name="album_genre_length_check",
        ),
        db.CheckConstraint(
            created_at <= datetime.now(timezone.utc),
            name="album_created_at_not_future",
        ),
    )

    def __repr__(self):
        return f"<Album {self.name}>"


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now(timezone.utc)
    )
    songs = db.relationship(
        "Song", secondary="playlist_song", backref=db.backref("playlists", lazy=True)
    )

    __table_args__ = (
        db.UniqueConstraint("name", "user_id", name="_playlist_name_user_uc"),
        db.CheckConstraint(
            db.func.length(name) >= 2, name="playlist_name_length_check"
        ),
        db.CheckConstraint(
            created_at <= datetime.now(timezone.utc),
            name="album_created_at_not_future",
        ),
    )


class PlaylistSong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey("playlist.id"), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey("song.id"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("playlist_id", "song_id", name="_playlist_song_uc"),
    )

    def __repr__(self):
        return f"<PlaylistSong {self.id}>"


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey("song.id"), nullable=False)
    rating_value = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "song_id", name="_rating_user_song_uc"),
        db.CheckConstraint(
            "rating_value >= 1 AND rating_value <= 5", name="_rating_value_range"
        ),
    )

    def __repr__(self):
        return f"<Rating {self.id}>"


class Flag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey("song.id"), nullable=False)
    reason = db.Column(db.String(255), nullable=True)

    __table_args__ = (
        db.UniqueConstraint("user_id", "song_id", name="_flag_user_song_uc"),
    )

    def __repr__(self):
        return f"<Flag {self.id}>"
