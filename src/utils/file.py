import os
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
from flask import current_app
from typing import Optional, Tuple

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
UPLOAD_FOLDER = "../static/uploads/verification_docs"


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_verification_document(file) -> Tuple[Optional[str], Optional[str]]:
    """
    Save verification document and return the filename
    Returns: (filename, error_message)
    """
    if not file:
        return None, "No file provided"

    if not allowed_file(file.filename):
        return (
            None,
            f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Create unique filename
    original_filename = secure_filename(file.filename)
    extension = original_filename.rsplit(".", 1)[1].lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4().hex[:8])
    filename = f"verification_{timestamp}_{unique_id}.{extension}"

    # Ensure upload directory exists
    os.makedirs(os.path.join(current_app.root_path, UPLOAD_FOLDER), exist_ok=True)

    try:
        file_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
        file.save(file_path)
        return filename, None
    except Exception as e:
        return None, f"Error saving file: {str(e)}"


def delete_verification_document(filename: str) -> bool:
    """Delete a verification document"""
    if not filename:
        return False

    try:
        file_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False
