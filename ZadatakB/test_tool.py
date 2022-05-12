import base64
import requests

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

#add_item('gun', './example_images/gun.jpg')
get_similarity('./example_images/cola_2.jpg', 3)

