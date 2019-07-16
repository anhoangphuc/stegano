import os
import json
from PIL import Image

from flask import render_template, jsonify, request, flash, session
from werkzeug.utils import secure_filename

from app import app
from full_image import convert, encode
import utils


IMAGE_DIR = os.path.join(os.getcwd(), 'app', 'static', 'app_image')

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/processImage', methods=['POST', 'GET'])
def process_image():
    image = request.files['image']
    session['image_type'] = image.filename.split('.')[1]
    filename = secure_filename('original.' + session['image_type'])
    original_image = os.path.join(IMAGE_DIR, filename)
    image.save(original_image)

    # Convert image to gray pytorch image format
    gray_image, size_of_image, message_length = convert(original_image)
    gray_image_filename = os.path.join(IMAGE_DIR, f'gray.{session["image_type"]}')
    gray_image.save(gray_image_filename)
    b64_image = utils.encode_base64(gray_image_filename)

    return jsonify({
        'width': size_of_image[0],
        'height': size_of_image[1],
        'message_length': message_length,
        'b64_image': b64_image.decode(),
        'image_type': session['image_type'],
    })

@app.route('/encodeImage', methods=['POST'])
def encode_image():
    config_type = request.get_json()['config_type']
    data = encode(config_type)
    encoded_image_filename = os.path.join(IMAGE_DIR, f'encode.{session["image_type"]}')
    encoded_image = data['stego_image']
    encoded_image.save(encoded_image_filename)
    b64_image = utils.encode_base64(encoded_image_filename)
    return jsonify({
        'b64_image': b64_image.decode(),
        'image_type': session['image_type'],
    })

@app.route('/stegaimage', methods=['GET', 'POST'])
def stega_image():
    return render_template('stega_image.html')

@app.route('/hardware', methods=['GET', 'POST'])
def get_hardware():
    return render_template('hardware.html')

@app.route('/detail', methods=['GET', 'POST'])
def detail():
    return render_template('detail.html')

@app.route('/viewMessage', methods=['GET', 'POST'])
def view_message():
    data = utils.load_message()
    message_dir = os.path.join(IMAGE_DIR, 'message.jpg')
    decoded_dir = os.path.join(IMAGE_DIR, 'decoded.jpg')
    utils.visual_message(data['message'], message_dir)
    utils.visual_message(data['decoded_message'], decoded_dir)
    new_data = {}
    new_data['accr'] = data['accr']
    new_data['message_length'] = data['message_length']
    new_data['bit_error'] = data['bit_error']
    new_data['message'] = utils.encode_base64(message_dir).decode()
    new_data['decoded_message'] = utils.encode_base64(decoded_dir).decode()
    return jsonify(new_data)

@app.route('/picture', methods=['GET', 'POST'])
def picture():
    return render_template('picture.html')

@app.route('/hidepicture', methods=['GET', 'POST'])
def hidepicture():
    # save the original picture to dir
    image = request.files['image']
    session['image_type'] = image.filename.split('.')[1]
    filename = secure_filename('original.' + session['image_type'])
    original_image = os.path.join(IMAGE_DIR, filename)
    image.save(original_image)

    # convert picture to grayscale
    return jsonify({'filename': original_image})
