import numpy as np
import cv2
import base64
from tensorflow.keras.models import load_model
from mediapipe.solutions.holistic import Holistic 
from config import actions

model = load_model('model.keras')
colors = [(245, 117, 16), (117, 245, 16), (16, 117, 245)]
holistic = Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)

threshold = 0.5


def detect(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = model.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return results


def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33 * 4)
    face = np.array([[res.x, res.y, res.z] for res in results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(468 * 3)
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21 * 3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21 * 3)
    return np.concatenate([pose, face, lh, rh])


class PredictionModel:

    def __init__(self):
        self.sentence = []
        self.predictions = []

    async def predictISL(self, frames):
        sequence = []
        for frame in frames:
            imgdata = base64.b64decode(frame)
            imgdata = np.asarray(imgdata, dtype=np.uint8)
            image = cv2.imdecode(imgdata, 0)
            image, results = detect(image)
            keypoints = extract_keypoints(results)
            sequence.append(keypoints)

        res = model.predict(np.expand_dims(sequence, axis=0))[0]
        argmax = np.argmax(res)
        action = actions[argmax]

        self.predictions.append(argmax)
        if len(sentence) == 0 or action != sentence[-1]:
            if res[argmax] > threshold:
                self.sentence.append(action)
                return action

        
