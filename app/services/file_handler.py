import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app, has_request_context
from typing import List, Dict, Any

class FileHandler:
    def __init__(self, upload_folder=None):
        """
        Initialize FileHandler with custom or default upload folder
        
        Args:
            upload_folder (str, optional): Custom upload folder path. 
                                           Defaults to app config upload folder.
        """
        # If no upload_folder is provided, use a default path
        if upload_folder:
            self.upload_folder = upload_folder
        else:
            # Try to get from current_app config if in application context
            try:
                self.upload_folder = current_app.config.get(
                    'UPLOAD_FOLDER', 
                    os.path.join(os.path.dirname(__file__), 'uploads')
                )
            except RuntimeError:
                # Fallback to a default path if not in application context
                self.upload_folder = os.path.join(os.path.dirname(__file__), 'uploads')
        
        # Ensure upload directory exists
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def allowed_file(self, filename: str, allowed_extensions: List[str] = None) -> bool:
        """
        Check if the file extension is allowed
        
        Args:
            filename (str): Name of the file to check
            allowed_extensions (List[str], optional): List of allowed extensions. 
                                                     Defaults to config's ALLOWED_EXTENSIONS.
        
        Returns:
            bool: True if file is allowed, False otherwise
        """
        # Try to get allowed extensions from current_app, fallback to default
        try:
            allowed_extensions = allowed_extensions or current_app.config.get(
                'ALLOWED_EXTENSIONS', 
                {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xml', 'json'}
            )
        except RuntimeError:
            allowed_extensions = allowed_extensions or {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xml', 'json'}
        
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """
        Generate a unique filename to prevent overwriting
        
        Args:
            original_filename (str): Original filename
        
        Returns:
            str: Unique filename
        """
        # Get file extension
        file_ext = original_filename.rsplit('.', 1)[1].lower()
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        return unique_filename
    
    def save_file(self, file, custom_filename: str = None) -> Dict[str, Any]:
        """
        Save uploaded file with optional custom filename
        
        Args:
            file: File object from Flask request
            custom_filename (str, optional): Custom filename to use
        
        Returns:
            Dict containing file details
        
        Raises:
            ValueError: If file is invalid
        """
        if not file:
            raise ValueError("No file provided")
        
        # Secure the original filename
        original_filename = secure_filename(file.filename)
        
        # Check if file is allowed
        if not self.allowed_file(original_filename):
            raise ValueError(f"File type not allowed: {original_filename}")
        
        # Use custom filename or generate unique one
        if custom_filename:
            filename = secure_filename(custom_filename)
        else:
            filename = self.generate_unique_filename(original_filename)
        
        # Full path for saving
        filepath = os.path.join(self.upload_folder, filename)
        
        # Save the file
        file.save(filepath)
        
        return {
            'original_filename': original_filename,
            'saved_filename': filename,
            'filepath': filepath,
            'file_extension': filename.rsplit('.', 1)[1].lower(),
            'file_size': os.path.getsize(filepath)
        }
    
    def delete_file(self, filepath: str) -> bool:
        """
        Delete a file from the filesystem
        
        Args:
            filepath (str): Full path to the file
        
        Returns:
            bool: True if file was deleted, False if file not found
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            current_app.logger.error(f"Error deleting file {filepath}: {str(e)}")
            return False
    
    def list_files(self, extension: str = None) -> List[Dict[str, Any]]:
        """
        List files in the upload directory
        
        Args:
            extension (str, optional): Filter by file extension
        
        Returns:
            List of file details
        """
        files = []
        for filename in os.listdir(self.upload_folder):
            filepath = os.path.join(self.upload_folder, filename)
            
            # Skip if not a file
            if not os.path.isfile(filepath):
                continue
            
            # Filter by extension if provided
            if extension and not filename.lower().endswith(extension.lower()):
                continue
            
            files.append({
                'filename': filename,
                'filepath': filepath,
                'file_extension': filename.rsplit('.', 1)[1].lower(),
                'file_size': os.path.getsize(filepath),
                'created_at': os.path.getctime(filepath)
            })
        
        return files