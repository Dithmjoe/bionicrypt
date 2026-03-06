import dlib
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

# Load face detector and landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Folder containing test images
image_folder = "test_images"
ground_truth_folder = "ground_truth"   # each txt file contains 68 (x,y) points

nme_list = []
image_names = []

def calculate_nme(pred_points, gt_points):
    pred_points = np.array(pred_points)
    gt_points = np.array(gt_points)

    # Inter-ocular distance (distance between eye centers)
    left_eye = np.mean(gt_points[36:42], axis=0)
    right_eye = np.mean(gt_points[42:48], axis=0)
    inter_ocular_distance = np.linalg.norm(left_eye - right_eye)

    error = np.linalg.norm(pred_points - gt_points, axis=1)
    nme = np.mean(error) / inter_ocular_distance
    return nme

for file in os.listdir(image_folder):
    if file.endswith(".jpg") or file.endswith(".png"):
        img_path = os.path.join(image_folder, file)
        img = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = detector(gray)

        if len(faces) > 0:
            shape = predictor(gray, faces[0])
            pred_points = [(shape.part(i).x, shape.part(i).y) for i in range(68)]

            # Load ground truth points
            gt_file = os.path.join(ground_truth_folder, file.split('.')[0] + ".txt")
            gt_points = []
            with open(gt_file, 'r') as f:
                for line in f:
                    x, y = map(float, line.strip().split())
                    gt_points.append((x, y))

            nme = calculate_nme(pred_points, gt_points)
            nme_list.append(nme)
            image_names.append(file)

# Plot NME graph
plt.figure()
plt.plot(range(len(nme_list)), nme_list)
plt.xlabel("Image Index")
plt.ylabel("Normalized Mean Error (NME)")
plt.title("Performance Evaluation of shape_predictor_68_face_landmarks")
plt.show()