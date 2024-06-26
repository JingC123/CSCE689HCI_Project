from flask import Flask, jsonify, request
from flask_cors import CORS
import os

#from dotenv import load_dotenv
import requests
import json
# Load environment variables
version = "?api-version=2023-02-01-preview&modelVersion=latest"
endpoint = ""
key = ""
img_map = dict()


def get_image_embedding(image):
    with open(image, "rb") as img:
        data = img.read()

    # Vectorize Image API

    vectorize_img_url = endpoint + "retrieval:vectorizeImage" + version

    headers = {
        "Content-type": "application/octet-stream",
        "Ocp-Apim-Subscription-Key": key
    }

    try:
        r = requests.post(vectorize_img_url, data=data, headers=headers)

        if r.status_code == 200:
            image_vector = r.json()["vector"]
            return image_vector
        else:
            print(f"An error occurred while processing {image}. Error code: {r.status_code}.")

    except Exception as e:
        print(f"An error occurred while processing {image}: {e}")

    return None

# image_filename = "689class/Hospital/mufid-majnun-J12RfFH-2ZE-unsplash.jpg"
# image_vector = get_image_embedding(image_filename)
# image_filename2 = "689class/school/dom-fou-YRMWVcdyhmI-unsplash.jpg"
# image_vector2 = get_image_embedding(image_filename2)
#print(image_vector)

def get_text_embedding(prompt):
    text = {'text': prompt}

    # Image retrieval API
    vectorize_txt_url = endpoint + "retrieval:vectorizeText" + version

    headers = {
        'Content-type': 'application/json',
        'Ocp-Apim-Subscription-Key': key
    }

    try:
        r = requests.post(vectorize_txt_url, data=json.dumps(text), headers=headers)

        if r.status_code == 200:
            text_vector = r.json()['vector']
            return text_vector
        else:
            print(f"An error occurred while processing the prompt '{text}'. Error code: {r.status_code}.")

    except Exception as e:
        print(f"An error occurred while processing the prompt '{text}': {e}")

    return None

# text_prompt = "school"
# text_vector = get_text_embedding(text_prompt)

from numpy import dot
from numpy.linalg import norm

def get_cosine_similarity(vector1, vector2):
    return dot(vector1, vector2) / (norm(vector1) * norm(vector2))

# similarity = get_cosine_similarity(image_vector, text_vector)
# print(similarity)
# similarity2 = get_cosine_similarity(image_vector2, text_vector)
# print(similarity2)


def generate_image_vals(text_vector):
    img_vectors = []
    for filename in os.listdir("photos"):
        img_filename = "photos/" + filename
        image_vector = img_map[filename[:-4]]
        similarity = get_cosine_similarity(image_vector, text_vector)
        img_vectors.append((img_filename, similarity))
    return img_vectors

def get_most_k_filenames(prompt, k):
    sorted_img = sorted(generate_image_vals(get_text_embedding(prompt)), key=lambda x: x[1], reverse=True)
    result = []
    for img in sorted_img:
        result.append(img[0])
    return result[:k]

def generate_image_map():
    for filename in os.listdir("photos"):
        img_filename = "photos/" + filename
        image_vector = get_image_embedding(img_filename)
        img_map[filename[:-4]]=image_vector
    return

app = Flask(__name__)
CORS(app)



@app.route('/search', methods = ["POST"])
def searchImage():
    data = json.loads(request.data)
    description = data['desc']
    return jsonify({'photos': get_most_k_filenames(description, 3)}) 


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


# pre load all the picture to cache when server start
with app.app_context():
    generate_image_map()

if __name__ == '__main__':
    app.run(debug=False)
    
