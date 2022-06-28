import base64
import requests


url_add = 'http://localhost:8000/items/'
url_cat = 'http://localhost:8000/categories/'


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
    r = requests.post(url_add, json = json)
    print(r.status_code, r.text)

def get_all_items():
    r = requests.get(url_add, params = {'itemName': 'nepostojeci item'})
    print(r.text)

def delete_item(uuid):
    #json = {'uuid': uuid}
    json = {'name' : uuid}
    r = requests.delete(url_add, json = json)
    print(r.text)

def update_item(uuid, new_name = '', new_category = '', new_image = ''):
    if new_category != '':
        json = {'uuid': uuid, 'name': new_name}
    elif new_name != '':
        json = {'uuid': uuid, 'category': new_category}
    elif new_image != '':
        img = encode_image(new_image)
        json = {'uuid': uuid, 'imageBase64': img.decode('utf-8')}
    r = requests.put(url_add, json = json)
    print(r.text)

def add_category(category_name):
    json = {'categoryName' : category_name}
    r = requests.post(url_cat, json = json)
    print(r.status_code, r.text)

#add_category('Gazirana pića')
#add_category('Sokovi u prahu')
#add_category('Alkohol')
#add_item('Coca cola', '../example_images/coca_cola.jpg', 'Gazirana pića')
#add_item('Sprite', '../example_images/sprite.jpg', 'Gazirana pića')
#add_item('Cedevita', '../example_images/cedevita.jpg', 'Sokovi u prahu')
#add_item('Cevitana', '../example_images/cevitana.jpg', 'Sokovi u prahu')
#add_item('Jim Beam', '../example_images/jim_beam.jpg', 'Alkohol')
#add_item('Sax', '../example_images/sax_gin.jpeg', 'Alkohol')
#add_item('Pelin', '../example_images/badel_pelin.png', 'Alkohol')

get_similarity('../example_images/cola_test.jpg', 3)
