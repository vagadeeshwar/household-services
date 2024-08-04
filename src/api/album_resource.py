from flask_restful import Resource, reqparse, abort, marshal_with
from ..models import Album, User
from .schemas import AlbumSchema
from flask_login import login_required, current_user
from ..database import db

album_schema = AlbumSchema()
albums_schema = AlbumSchema(many=True)


class AlbumListResource(Resource):
    @marshal_with(albums_schema)
    def get(self):
        albums = Album.query.all()
        return albums

    @login_required
    @marshal_with(album_schema)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str, required=True)
        parser.add_argument("description", type=str)
        parser.add_argument("genre", type=str)
        args = parser.parse_args()

        if Album.query.filter_by(name=args["name"]).first():
            abort(409, message="Album name already exists")

        album = Album(
            name=args["name"],
            user_id=current_user.id,
            description=args["description"],
            genre=args["genre"],
        )
        db.session.add(album)
        db.session.commit()

        return album, 201


class AlbumResource(Resource):
    @marshal_with(album_schema)
    def get(self, album_id):
        album = Album.query.get(album_id)
        if not album:
            abort(404, message="Album not found")
        return album

    @login_required
    @marshal_with(album_schema)
    def put(self, album_id):
        album = Album.query.get(album_id)
        if not album:
            abort(404, message="Album not found")

        if album.user_id != current_user.id:
            abort(403, message="You are not authorized to update this album")

        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str)
        parser.add_argument("description", type=str)
        parser.add_argument("genre", type=str)
        args = parser.parse_args()

        if args["name"] and Album.query.filter_by(name=args["name"]).first():
            abort(409, message="Album name already exists")

        album.name = args["name"] or album.name
        album.description = args["description"] or album.description
        album.genre = args["genre"] or album.genre

        db.session.commit()
        return album

    @login_required
    def delete(self, album_id):
        album = Album.query.get(album_id)
        if not album:
            abort(404, message="Album not found")

        if album.user_id != current_user.id:
            abort(403, message="You are not authorized to delete this album")

        db.session.delete(album)
        db.session.commit()
        return "", 204


class UserAlbumListResource(Resource):
    @marshal_with(albums_schema)
    def get(self, user_id):
        user = User.query.get(user_id)
        if not user:
            abort(404, message="User not found")

        albums = Album.query.filter_by(user_id=user_id).all()
        return albums
