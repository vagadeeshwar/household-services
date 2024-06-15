from flask import request, current_app
from flask_restful import Resource, reqparse, abort, marshal_with
from ..models import Song, Album
from .schemas import SongSchema
from ..utils import generate_filename
from flask_login import login_required
from ..database import db
import os

song_schema = SongSchema()
songs_schema = SongSchema(many=True)


class SongListResource(Resource):
    @marshal_with(songs_schema)
    def get(self):
        songs = Song.query.all()
        return songs

    @login_required
    @marshal_with(song_schema)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str, required=True)
        parser.add_argument("album_id", type=int, required=True)
        parser.add_argument("lyrics", type=str)
        parser.add_argument("genre", type=str)
        parser.add_argument("duration", type=str, required=True)
        args = parser.parse_args()

        album = Album.query.get(args["album_id"])
        if not album:
            abort(400, message="Invalid album ID")

        if Song.query.filter_by(name=args["name"]).first():
            abort(409, message="Song name already exists")

        song = Song(
            name=args["name"],
            album_id=args["album_id"],
            lyrics=args["lyrics"],
            genre=args["genre"],
            duration=args["duration"],
        )
        db.session.add(song)
        db.session.commit()

        return song, 201


class SongResource(Resource):
    @marshal_with(song_schema)
    def get(self, song_id):
        song = Song.query.get(song_id)
        if not song:
            abort(404, message="Song not found")
        return song

    @login_required
    @marshal_with(song_schema)
    def put(self, song_id):
        song = Song.query.get(song_id)
        if not song:
            abort(404, message="Song not found")

        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str)
        parser.add_argument("album_id", type=int)
        parser.add_argument("lyrics", type=str)
        parser.add_argument("genre", type=str)
        parser.add_argument("duration", type=str)
        args = parser.parse_args()

        if args["name"] and Song.query.filter_by(name=args["name"]).first():
            abort(409, message="Song name already exists")

        album = Album.query.get(args["album_id"])
        if args["album_id"] and not album:
            abort(400, message="Invalid album ID")

        song.name = args["name"] or song.name
        song.album_id = args["album_id"] or song.album_id
        song.lyrics = args["lyrics"] or song.lyrics
        song.genre = args["genre"] or song.genre
        song.duration = args["duration"] or song.duration

        db.session.commit()
        return song

    @login_required
    def delete(self, song_id):
        song = Song.query.get(song_id)
        if not song:
            abort(404, message="Song not found")

        db.session.delete(song)
        db.session.commit()
        return "", 204


class SongUploadResource(Resource):
    @login_required
    def post(self):
        if "audio" not in request.files:
            abort(400, message="No audio file provided")

        audio = request.files["audio"]
        if audio.filename == "":
            abort(400, message="No audio file selected")

        filename = generate_filename(audio.filename)
        audio_path = os.path.join(current_app.config["AUDIO_FOLDER"], filename)
        audio.save(audio_path)

        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str, required=True)
        parser.add_argument("album_id", type=int, required=True)
        parser.add_argument("lyrics", type=str)
        parser.add_argument("genre", type=str)
        parser.add_argument("duration", type=str, required=True)
        args = parser.parse_args()

        album = Album.query.get(args["album_id"])
        if not album:
            abort(400, message="Invalid album ID")

        if Song.query.filter_by(name=args["name"]).first():
            abort(409, message="Song name already exists")

        song = Song(
            name=args["name"],
            album_id=args["album_id"],
            lyrics=args["lyrics"],
            genre=args["genre"],
            duration=args["duration"],
            audio_path=audio_path,
        )
        db.session.add(song)
        db.session.commit()

        return {"message": "Song uploaded successfully"}, 201
