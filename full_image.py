'''
This module receive an image of full size and return stega
'''

import os
from PIL import Image
import pickle

import torch
from torchvision import transforms
import numpy as np
from flask import session

import utils
from model.hidden import Hidden
from noise_layers.noiser import Noiser


def reshape_image(image: Image):
    img = image.convert('L')
    new_height = img.size[1] // 16 * 16
    new_width = img.size[0] // 16 * 16
    img = img.resize((new_width, new_height), Image.ANTIALIAS)
    return img

def crop_image(image):
    list_image_cropped = []
    position_cropped = []
    width, height = image.size
    print(width, height)
    for i in range(0, width, 16):
        for j in range(0, height, 16):
            list_image_cropped.append(image.crop((i, j, i + 16, j + 16)))
            position_cropped.append([i, j])

    return (list_image_cropped, position_cropped)

def load_model(config_file, device):
    config_folder = os.path.join('config_folder', config_file)
    option_file = os.path.join(config_folder, 'options.pickle')
    checkpoint_file = os.path.join(config_folder, 'checkpoint.pyt')

    checkpoint = torch.load(checkpoint_file, map_location='cpu')
    _, hidden_config, noise_config = utils.load_options(option_file)
    noiser = Noiser(noise_config, device)
    model = Hidden(hidden_config, device, noiser, tb_logger=None)
    utils.model_from_checkpoint(model, checkpoint)

    return model

def get_transform():
    return transforms.Compose([
        transforms.Grayscale(1),
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5])
    ])

def encode(config_type):
    source_image = utils.get_gray_image()
    print('Source image', source_image)
    image = Image.open(source_image)
    list_image_cropped, position_cropped = crop_image(image)

    full_encoded_image = torch.zeros(image.size[::-1])
    full_encoded_image.unsqueeze_(0)
    print(full_encoded_image.shape)

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = load_model(f'model_{config_type}', device)
    transform = get_transform()
    
    total_message = np.array([])
    total_decoded_message = np.array([])
    for i, cropped_image in enumerate(list_image_cropped):
        print(i)
        posy, posx = position_cropped[i]
        # print(i, posx, posy)
        image = transform(cropped_image)
        image = image.to(device)
        message = torch.Tensor(np.random.choice([0, 1], (1, 52))).to(device)
        image.unsqueeze_(0)
        losses, (encoded_image, _, decoded_message) = model.validate_on_batch([image, message])
        encoded_image.squeeze_(0)
        full_encoded_image[:, posx:posx+16, posy:posy+16] = encoded_image[:, :, :]
        decoded_message = decoded_message.detach().cpu().squeeze().numpy().\
                            round().clip(0, 1)
        total_message = np.append(total_message, message.detach().cpu().\
                                  squeeze().numpy())
        total_decoded_message = np.append(total_decoded_message, decoded_message)
        
    full_image = full_encoded_image.squeeze_(0).cpu().numpy()
    full_image = (full_image + 1) * 127.5
    full_image = np.clip(full_image, 0, 255).astype(np.uint8)
    print(full_image.shape)
    stego_image = Image.fromarray(full_image)
    bit_error = np.sum(np.abs(total_message - total_decoded_message))

    error_detail = {
        'message_length': len(total_message),
        'bit_error': bit_error,
        'message': total_message,
        'decoded_message': total_decoded_message,
        'accr': bit_error / len(total_message),
    }

    pickle.dump(error_detail, open('detail', 'wb'))

    return {'stego_image': stego_image}

def convert(source_image):
    image = Image.open(source_image)
    image = reshape_image(image)
    gray_image = get_transform()(image)
    gray_image = gray_image.squeeze_(0).numpy()
    gray_image = (gray_image + 1) * 127.5
    gray_image = np.clip(gray_image, 0, 255).astype(np.uint8)
    original_image = Image.fromarray(gray_image)
    width, height = original_image.size
    message_length = ((width // 16) * (height // 16)) * 52
    return (original_image, original_image.size, message_length)

if __name__ == '__main__':
    pass
    # main()
    # convert()
