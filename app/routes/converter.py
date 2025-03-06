from flask import Blueprint, request, jsonify, send_file, render_template, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.data_converter import DataConverterService
import os

converter_route = Blueprint('converter', __name__)
converter_service = DataConverterService()

@converter_route.route('/convert', methods=['POST'])
@jwt_required()
def convert_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    current_user_id = get_jwt_identity()
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        # Convert file
        conversion_result = converter_service.convert_file(file, current_user_id)
        
        return jsonify({
            'message': 'File converted successfully',
            'result': conversion_result
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@converter_route.route('/download/<path:filename>', methods=['GET'])
@jwt_required()
def download_file(filename):
    try:
        return send_file(filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

@converter_route.route('/conversion-result')
@jwt_required()
def conversion_result():
    return render_template('conversion-result.html')

@converter_route.route('/download', methods=['GET'])
@jwt_required()
def api_download():
    file_path = request.args.get('file')
    if not file_path:
        return jsonify({'error': 'No file specified'}), 400
    
    try:
        # Security check - ensure the file exists
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
            
        filename = os.path.basename(file_path)
        return send_file(file_path, 
                        as_attachment=True, 
                        download_name=filename)
    except Exception as e:
        current_app.logger.error(f"Download error: {str(e)}")
        return jsonify({'error': 'File download failed'}), 500