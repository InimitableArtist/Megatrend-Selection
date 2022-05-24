import base64
from fileinput import filename
import requests
import os

url_add = 'http://localhost:5000/item'
url_similar = 'http://localhost:5000/similar'

def encode_image(img_path):
    with open(img_path, 'rb') as f:
        encoded_string = base64.b64encode(f.read())
    return encoded_string


def add_item(item_name, img_path):
    img = encode_image(img_path)
    json = {'itemName': item_name, 'imageBase64': img.decode('utf-8')}
    r = requests.post(url_add, json = json)
    print(r.status_code)

def get_similarity(img_path, n):
    img = encode_image(img_path)
    json = {'imageBase64': img.decode('utf-8'), 'n': str(n)}
    r = requests.post(url_similar, json = json)
    print(r.text)

def add_person(name):
    PATH = './example_images/' + name + '/'
    filenames = os.listdir(PATH)
    for filename in filenames:
        path = os.path.join(PATH, filename)
        add_item(name, path)

#add_person('matej')
#add_person('matea')
#add_item('gun', './example_images/gun.jpg')
#add_item('cola', './example_images/cola.jpg')
#add_item('cockta', './example_images/cockta.jpg')
#add_item('fanta', './example_images/fanta.jpg')
#add_item('sprite', './example_images/sprite.jpg')
#add_item('face', './example_images/face.jpg')
#add_item('amber_1', './example_images/slika_1.jpg')
get_similarity('./example_images/matej_example_1.jpg', 1)
#add_item('cola', './example_images/cola_4.jpg')

