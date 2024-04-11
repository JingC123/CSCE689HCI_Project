from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/photos')
def get_photos():
    folder_path = 'photos'
    if not folder_path:
        return jsonify({'error': 'Folder path not provided'}), 400

    if not os.path.exists(folder_path):
        return jsonify({'error': 'Folder path does not exist'}), 404

    photos = []
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            photos.append(os.path.join(folder_path, file_name))

    return jsonify({'photos': photos})

if __name__ == '__main__':
    app.run(debug=True)
