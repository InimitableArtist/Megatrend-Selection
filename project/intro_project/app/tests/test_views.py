from django.test import TestCase
from app.views import ListCategories, ListItems
from rest_framework.test import APIRequestFactory
from app.models import Category, Item
import base64

def encode_image(img_path = '/src/app/tests/test_images/cola.jpg'):
    with open(img_path, 'rb') as f:
        encoded_string = base64.b64encode(f.read())
    return encoded_string.decode('utf-8')

UUID = 'ea2d3388-f39b-11ec-8b74-54ee7575dad0'

class ItemTestClass(TestCase):

    @classmethod
    def setUpTestData(cls):
        Category.objects.create(name = 'Gazirana pića', 
        uuid = '971f7974-f394-11ec-8a0b-54ee7575dad0')
        Category.objects.create(name = 'Alkohol', 
        uuid = '77919fa2-f3be-11ec-969e-cc3d820ad133')
        Item.objects.create(name = 'cockta', uuid = 'ea2d3388-f39b-11ec-8b74-54ee7575dad0',
        category = Category.objects.get(name = 'Gazirana pića'))

    def setUp(self):
        self.factory = APIRequestFactory()

    #POST tests
    def test_add_item_no_image(self):
        data = {'itemName': 'cola',
                'categoryName': 'Gazirana pića'}
        request = self.factory.post('/items/', data = data, format = 'json')
        response = ListItems.as_view()(request)

        items = Item.objects.all()
        item = items[1]
        self.assertEqual(response.status_code, 201)
        self.assertEqual(item.name, 'cola')
        self.assertEqual(item.category.name, 'Gazirana pića')
        self.assertEqual(items.count(), 2)

    def test_add_item_image(self):
        data = {'itemName' : 'cola',
                'categoryName': 'Gazirana pića',
                'imageBase64': encode_image()}

        request = self.factory.post('/items/', data = data, format = 'json')
        response = ListItems.as_view()(request)

        items = Item.objects.all()
        item = items[1]
        self.assertEqual(response.status_code, 201)
        self.assertEqual(item.name, 'cola')
        self.assertEqual(item.category.name, 'Gazirana pića')
        self.assertEqual(items.count(), 2)

    def test_add_item_invalid_category(self):
        data = {'itemName': 'cola',
                'categoryName': 'nepostojeca kategorija'}

        request = self.factory.post('/items/', data = data, format = 'json')
        response = ListItems.as_view()(request)
        self.assertEqual(response.status_code, 404)
        items = Item.objects.all()
        self.assertEqual(items.count(), 1)

    def test_invalid_parameters(self):
        data = {'itemName': 'cola'}

        request = self.factory.post('/items/', data = data, format = 'json')
        response = ListItems.as_view()(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Item.objects.all().count(), 1)

    def test_invalid_b64img_string(self):
        data = {'itemName': 'cola',
                'categoryName': 'Gazirana pića',
                'imageBase64': base64.b64encode(b'randomstring').decode('utf-8')}

        request = self.factory.post('/items/', data = data, format = 'json')
        response = ListItems.as_view()(request)

        items = Item.objects.all()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(items.count(), 1)

    def test_similarity_n_too_big(self):
        data = {'imageBase64': encode_image(),
                'n': '100'}
        request = self.factory.post('/items/', data = data, format = 'json')
        response = ListItems.as_view()(request)

        self.assertEqual(response.status_code, 400)
        
    #GET tests
    def test_get_all_items(self):
        request = self.factory.get('/items/')
        response = ListItems.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), Item.objects.all().count())

    def test_get_items_by_name(self):
        item_name = 'cockta'
        request = self.factory.get('/items/', params = {'itemName': item_name})

        response = ListItems.as_view()(request)
        items = Item.objects.filter(name = item_name)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), items.count())

    #Ovo ne radi iz nekog razloga.
    def test_get_invalid_name(self):
        item_name = 'nepostojeci item'
        request = self.factory.get('/items/', params = {'itemName': item_name})
    
        response = ListItems.as_view()(request)
     
        self.assertEqual(response.status_code, 404)

    #DELETE tests
    def test_delete_item_by_uuid(self):
        data = {'uuid': UUID}
        
        request = self.factory.delete('/items/', data = data, format = 'json')
        response = ListItems.as_view()(request)

        items = Item.objects.all()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(items.count(), 0)

    def test_delete_items_by_name(self):
        name = 'cockta'
        Item.objects.create(name = 'cockta', uuid = '2b08814e-f3b1-11ec-969e-cc3d820ad133',
                            category = Category.objects.get(name = 'Gazirana pića'))

        data = {'itemName': name}
        request = self.factory.delete('/items/', data = data, format = 'json')
        response = ListItems.as_view()(request)

        items = Item.objects.all()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(items.count(), 0)

    
    def test_delete_non_existent_item(self):
        uuid = '2794722e-f3b2-11ec-969e-cc3d820ad133'
        data = {'uuid': uuid}

        request = self.factory.delete('/items/', data = data, format = 'json')
        response = ListItems.as_view()(request)

        items = Item.objects.all()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(items.count(), 1)

    #PUT tests
    def test_put_item_new_name(self):
        data = {'uuid': UUID, 'itemName' : 'NovoIme'}

        request = self.factory.put('/items/', data = data, format = 'json')
        response = ListItems.as_view()(request)

        item = Item.objects.get(uuid = UUID)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(item.name, 'NovoIme')

    def test_put_item_new_category(self):
        data = {'uuid': UUID, 'categoryName': 'Alkohol'}

        request = self.factory.put('/items/', data = data, format = 'json')
        response = ListItems.as_view()(request)

        item = Item.objects.get(uuid = UUID)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(item.category, Category.objects.get(name = 'Alkohol'))
    
    def test_put_item_new_image(self):
        data = {'uuid': UUID, 'imageBase64': encode_image()}

        request = self.factory.put('/items/', data = data, format = 'json')
        response = ListItems.as_view()(request)

        item = Item.objects.get(uuid = UUID)

        self.assertEqual(response.status_code, 201)
    
    def test_put_non_existent_category(self):
        data = {'uuid': UUID, 'categoryName': 'nepostojeca kategorija'}

        request = self.factory.put('/items/', data = data, format = 'json')
        response = ListItems.as_view()(request)

        item = Item.objects.get(uuid = UUID)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(item.category, Category.objects.get(name = 'Gazirana pića'))

    def test_put_invalid_image(self):
        
        data = {'uuid': UUID, 'imageBase64': base64.b64encode(b'randomstring').decode('utf-8')}

        request = self.factory.put('/items/', data = data, format = 'json')
        response = ListItems.as_view()(request)

        item = Item.objects.get(uuid = UUID)

        self.assertEqual(response.status_code, 400)

class CategoryTestClass(TestCase):


    
    @classmethod
    def setUpTestData(cls):
        Category.objects.create(name = 'Gazirana pića', 
        uuid = '971f7974-f394-11ec-8a0b-54ee7575dad0')

    def setUp(self):
        self.factory = APIRequestFactory()
    

    #GET tests
    def test_get_all_categories(self):
        request = self.factory.get('/categories/')
        response = ListCategories.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), Category.objects.all().count())

    #POST tests
    def test_create_new_category(self):
        data = {'categoryName': 'Alkohol'}

        request = self.factory.post('/categories/', data = data, format = 'json')
        response = ListCategories.as_view()(request)
        
        categories = Category.objects.all()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(categories.count(), 2)
        self.assertEqual(categories[1].name, 'Alkohol')

    def test_create_duplicate_category(self):
        data = {'categoryName' : 'Gazirana pića'}

        request = self.factory.post('/categories/', data = data, format = 'json')
        response = ListCategories.as_view()(request)

        categories = Category.objects.all()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(categories.count(), 1)


