import cv2
import dlib
import os

PREDICTOR_PATH = r"c:\Users\dithm\main project\final\bio_final\shape_predictor_68_face_landmarks.dat"
DEBUG_IMAGE = r"c:\Users\dithm\main project\final\bio_final\debug_no_face_detected.png"

def test_detection(image_path):
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return

    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply CLAHE to improve contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    
    detector = dlib.get_frontal_face_detector()
    
    orientations = [
        ("Original", gray),
        ("Flip H", cv2.flip(gray, 1)),
        ("Flip V", cv2.flip(gray, 0)),
        ("Flip HV", cv2.flip(gray, -1)),
        ("90 CW", cv2.rotate(gray, cv2.ROTATE_90_CLOCKWISE)),
        ("90 CCW", cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE)),
        ("180", cv2.rotate(gray, cv2.ROTATE_180))
    ]
    
    found = False
    for label, img in orientations:
        faces = detector(img, 2) # Upsample 2 times for better detection
        if len(faces) > 0:
            print(f"SUCCESS: Face detected in {label} orientation!")
            found = True
            break
            
    if not found:
        print("FAILURE: Still no face detected with improved methods.")

if __name__ == "__main__":
    test_detection(DEBUG_IMAGE)
