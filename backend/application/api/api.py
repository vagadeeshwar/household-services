from flask import Blueprint
from flask_restful import Api
from .user_resource import UserResource
# from .album_resource import AlbumResource, AlbumListResource
# from .song_resource import SongResource, SongListResource

api_bp = Blueprint("api", __name__)
api = Api(api_bp)

api.add_resource(UserResource, "/user/<int:user_id>")
# api.add_resource(UserListResource, "/users/<int:user_id>")
# api.add_resource(AlbumResource, "/album/<int:album_id>")
# api.add_resource(AlbumListResource, "/albums/<int:album_id>")
# api.add_resource(SongResource, "/song/<int:song_id>")
# api.add_resource(SongListResource, "/songs/<int:song_id>")
