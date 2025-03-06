from http import HTTPStatus

from flask import jsonify

from src import db


class APIResponse:
    """Unified API Response Handler"""

    @staticmethod
    def success(data=None, message=None, status_code=HTTPStatus.OK, pagination=None):
        response = {
            "status": "success",
            "status_code": status_code,
            "data": data,
        }
        if message:
            response["detail"] = message
        if pagination:
            response["pagination"] = pagination

        return jsonify(response), status_code

    @staticmethod
    def error(message, status_code=HTTPStatus.BAD_REQUEST, error_type=None):
        """
        Centralized error response method
        Also handles database rollback when needed
        """
        if status_code >= 500:  # Server errors
            db.session.rollback()

        response = {
            "status": "failure",
            "status_code": status_code,
            "detail": message,
            "error_type": error_type,
        }
        return jsonify(response), status_code


# Register error handler with Flask app
def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Handle all unhandled exceptions"""
        app.logger.error(f"Unhandled exception: {str(e)}")
        return APIResponse.error(
            message="An unexpected error occurred",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    @app.errorhandler(HTTPStatus.NOT_FOUND)
    def handle_404(e):
        """Handle 404 errors"""
        return APIResponse.error(
            message="Resource not found",
            status_code=HTTPStatus.NOT_FOUND,
        )

    @app.errorhandler(HTTPStatus.METHOD_NOT_ALLOWED)
    def handle_405(e):
        """Handle 405 errors"""
        return APIResponse.error(
            message="Method not allowed",
            status_code=HTTPStatus.METHOD_NOT_ALLOWED,
        )
