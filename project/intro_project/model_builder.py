import pickle
import time

from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.layers import Input
import tensorflow_hub as hub
import tensorflow as tf


MODULE_HANDLE = 'https://tfhub.dev/tensorflow/ssd_mobilenet_v2/2'
#MODULE_HANDLE = 'https://tfhub.dev/tensorflow/faster_rcnn/resnet50_v1_640x640/1'

PICKLE_PATH = './features_pickle.pkl'

#Create a pickle file where extracted features will be stored
def create_pickle_file(path):
    with open(path, 'wb') as f:
            pickle.dump({}, f) 

create_pickle_file(PICKLE_PATH)


#
#
#input_tensor = Input(shape = (256, 256, 3), name = 'image_input')
#model = InceptionV3(include_top = False, input_tensor = input_tensor, weights = 'imagenet', pooling = 'avg')
##model.trainable = False
#
#ts = int(time.time())
#file_path = "./soda_classifier/{}/".format(str(ts))
#model.save(filepath = file_path, save_format = 'tf')

#ts = int(time.time())
#detector = hub.load(MODULE_HANDLE)
#file_path = "./models/soda_detection/{}/".format(str(ts))
#tf.saved_model.save(detector, file_path)
