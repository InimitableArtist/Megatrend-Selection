import base64
import requests
import json

url = 'http://localhost:5000/classify'

def encode_image(img_path):
    with open(img_path, 'rb') as f:
        encoded_string = base64.b64encode(f.read())
    return encoded_string


def send_image(img_path):
    img = encode_image(img_path)
    json = {'imageBase64': img.decode('utf-8')}
    r = requests.post(url, json = json)
    print(r.text)

send_image('./example_images/3.png')

