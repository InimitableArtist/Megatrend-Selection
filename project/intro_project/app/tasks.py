import pickle

import numpy as np
from sklearn.neighbors import KNeighborsClassifier

from app.utils import get_embeddings

from .celery import app

PICKLE_PATH = 'features_pickle.pkl'

@app.task
def extract_features(base64img, item_name):
    embeddings = get_embeddings(base64img)

    with open(PICKLE_PATH, 'rb') as f:
        d = pickle.load(f)

    if item_name not in d.keys():
        d[item_name] = [embeddings, 1]
    
    else:
        saved_examples = d[item_name][1]
        f = (d[item_name][0] * saved_examples + embeddings) / (saved_examples + 1)
        d[item_name][0] = f
        d[item_name][1] = saved_examples + 1

    with open(PICKLE_PATH, 'wb') as f:
        pickle.dump(d, f)

@app.task
def classify_similar(base64img, n):
    current_embeddings = get_embeddings(base64img)

    with open(PICKLE_PATH, 'rb') as f:
        data = pickle.load(f)

    item_names = np.array(list(data.keys()))
    all_embeddings = np.array([i[0] for i in data.values()])
    neigh = KNeighborsClassifier(n_neighbors = n).fit(all_embeddings, item_names)
    predictions = neigh.kneighbors(current_embeddings.reshape(1, -1))
    distances = predictions[0][0]
    distances = [1/(1+d) for d in distances]
    indexes = predictions[1][0]
    labels = [item_names[i] for i in indexes]

    response = [{str(labels[i]) : str(distances[i])} for i in range(len(labels))]

    return response


    



    