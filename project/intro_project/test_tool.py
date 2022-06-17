import base64
from fileinput import filename
import requests
import os

url_add = 'http://localhost:8000/item/'
url_similar = 'http://localhost:8000/similar/'
url_all_items = 'http://localhost:8000/getitems/'

def encode_image(img_path):
    with open(img_path, 'rb') as f:
        encoded_string = base64.b64encode(f.read())
    return encoded_string


def add_item(item_name, img_path, category_name):
    img = encode_image(img_path)
    json = {'itemName': item_name, 'imageBase64': img.decode('utf-8'), 'categoryName' : category_name}
    r = requests.post(url_add, json = json)
    print(r.status_code)

def get_similarity(img_path, n):
    img = encode_image(img_path)
    json = {'imageBase64': img.decode('utf-8'), 'n': str(n)}
    r = requests.post(url_similar, json = json)
    print(r.text)

def get_all_items():
    r = requests.get(url_all_items)
    print(r.text)

#add_item('gun', '../example_images/gun.jpg', 'guns')
#add_item('cola', '../example_images/cola.jpg', 'gazirani sokovi')
#add_item('cola', '../example_images/cola_2.jpg', 'gazirani sokovi')
#add_item('cockta', '../example_images/cockta.jpg', 'alkoholna pica')
#add_item('fanta', '../example_images/fanta.jpg', 'gazirani sokovi')
#add_item('sprite', '../example_images/sprite.jpg', 'gazirani sokovi')
#get_similarity('../example_images/fanta.jpg', 6)


get_all_items()