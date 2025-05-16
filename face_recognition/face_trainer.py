import os
import cv2
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle

TARGET_WIDTH = 100
TARGET_HEIGHT = 100

def train_model():
    path = 'face_recognition/dataset'
    faces = []
    ids = []
    
    for image_path in os.listdir(path):
        if image_path.startswith('User.'):
            img_path = os.path.join(path, image_path)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            
            if img is not None:
                img = cv2.resize(img, (TARGET_WIDTH, TARGET_HEIGHT))
                id = int(image_path.split('.')[1])
                faces.append(img)
                ids.append(id)
    
    if len(faces) == 0:
        raise Exception("No faces found in dataset. Please register users first.")
    
    faces = np.array([face.reshape(-1) for face in faces])
    ids = np.array(ids)
    
    X_train, X_test, y_train, y_test = train_test_split(
        faces, ids, test_size=0.2, random_state=42
    )
    
    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(X_train, y_train)
    
    y_pred = knn.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model trained with accuracy: {accuracy:.2f}")
    
    if not os.path.exists('face_recognition/trainer'):
        os.makedirs('face_recognition/trainer')
    
    with open('face_recognition/trainer/knn_model.pkl', 'wb') as f:
        pickle.dump(knn, f)
    
    with open('face_recognition/trainer/model_params.pkl', 'wb') as f:
        pickle.dump((TARGET_HEIGHT, TARGET_WIDTH), f)
    
    return knn, (TARGET_HEIGHT, TARGET_WIDTH)