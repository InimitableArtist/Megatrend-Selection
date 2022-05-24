import pickle
import time

from tensorflow.keras.applications import InceptionV3, EfficientNetB0
from tensorflow.keras.layers import Input

PICKLE_PATH = './flask_server/features_pickle.pkl'

#Create a pickle file where extracted features will be stored
def create_pickle_file(path):
    with open(path, 'wb') as f:
            pickle.dump({}, f) 

create_pickle_file(PICKLE_PATH)


input_tensor = Input(shape = (224, 224, 3), name = 'image_input')
model = InceptionV3(include_top = False, input_tensor = input_tensor, weights = 'imagenet', pooling = 'avg')
#model.trainable = False

ts = int(time.time())
file_path = "./soda_classifier/{}/".format(str(ts))
model.save(filepath = file_path, save_format = 'tf')
