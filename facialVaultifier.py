import cv2
from cryptography.hazmat.primitives.asymmetric import ec
import dlib
import random
from itertools import combinations
import pickle
import hashlib
import utilities as util
import evaluator
import os

path=os.getcwd()

# Note: Install dlib and opencv: pip install dlib opencv-python
# Download shape_predictor_68_face_landmarks.dat from http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
# Unzip and place in the same directory

PREDICTOR_PATH = os.path.join(os.path.dirname(__file__), "shape_predictor_68_face_landmarks.dat")
PRIME = 2**521 - 1  # Large prime
QUANTIZE = 5  # Quantization step for tolerance
userName = "john cena"

def get_landmarks(image):
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(PREDICTOR_PATH)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Try multiple orientations
    orientations = [
        gray,  # Original
        cv2.flip(gray, 1),  # Horizontal flip
        cv2.flip(gray, 0),  # Vertical flip (Upside down)
        cv2.flip(gray, -1), # Both flips
        cv2.rotate(gray, cv2.ROTATE_90_CLOCKWISE),
        cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE)
    ]
    
    faces = None
    for img in orientations:
        faces = detector(img)
        if len(faces) > 0:
            gray = img # Use the successful orientation
            break
            
    if not faces or len(faces) == 0:
        # Save debug image
        cv2.imwrite("debug_no_face_detected.png", image)
        print("DEBUG: Face detection failed. Image saved to debug_no_face_detected.png")
        return None
        
    landmarks = predictor(gray, faces[0])
    points = []
    for i in range(68):
        x = landmarks.part(i).x // QUANTIZE
        y = landmarks.part(i).y // QUANTIZE
        point = x + y * (1000 // QUANTIZE)  # Assume image width <1000
        points.append(point)
    return sorted(set(points))  # Unique sorted list

def eval_poly(coeffs, p, key):
    result = coeffs[0]
    result = result*(p%key)
    return result

def lock(points, secret, key_len, key):
    max_point = max(points)
    min_point = min(points)
    # print(secret)
    coeffs = [secret]
    # print(coeffs)
    genuine_points = [(p, eval_poly(coeffs, p, key)) for p in points]
    chaff_count = len(points) * 5
    chaff_points = []
    used_x = set(points)
    while len(chaff_points) < chaff_count:
        x = random.randint(min_point, max_point)
        if x not in used_x:
            used_x.add(x)
            y = random.randint(int('1'+'0'*(key_len-1)), int('9'*key_len))
            true_y = eval_poly(coeffs, x, key)
            if y != true_y:
                chaff_points.append((x, y))
    vault = genuine_points + chaff_points
    random.shuffle(vault)
    return vault, hashlib.sha256(str(secret).encode()).hexdigest()  # Store hash for verification


def unlock(points, vault, key):
    candidate_points = []
    for x in points:
        for vx, vy in vault:
            if vx == x:
                candidate_points.append((vx, vy))
                break
    if not candidate_points:
        print("WHO THE HELL ARE YOU??")
        return None
    try:
        key_val = candidate_points[0][1]//(candidate_points[0][0]%key)
    except:
        print("WHO THE HELL ARE YOU??")
        return None
    hits = 0
    for i in range(1, len(candidate_points)):
        try:
            temp_key = candidate_points[i][1]//(candidate_points[i][0]%key_val)
            if temp_key==key_val:
                hits+=1
        except Exception as e:
            print(e)
            print(candidate_points[i][0]) 
            print(candidate_points[i][1])
    if hits>len(candidate_points)-10:
        return key_val
    return None

def capture_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error opening camera")
        return None
    print("Press 'c' to capture")
    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imshow('Capture', frame)
            key = cv2.waitKey(1)
            if key == ord('c'):
                cap.release()
                cv2.destroyAllWindows()
                return frame
        else:
            cap.release()
            cv2.destroyAllWindows()
            return None

def verifier(image, THE_KEY):
    if image is None:
        print("Capture failed")
    else:
        points = get_landmarks(image)
        if points is None:
            print("No face detected")
        else:
            try:
                with open(os.path.join(path, "vault.pkl"), "rb") as f:
                    vault, stored_hash = pickle.load(f)
                util.writer("")
                for j in vault:
                    util.appender(str(j))
                recovered_secret = unlock(points, vault, THE_KEY)
                if recovered_secret is not None:
                    recovered_hash = hashlib.sha256(str(recovered_secret).encode()).hexdigest()
                    if recovered_hash == stored_hash:
                        print("Verification successful. Secret key:", recovered_secret)
                        return recovered_secret
                    else:
                        print("Verification failed.",recovered_secret)
                else:
                    print("Verification failed.")
            except FileNotFoundError:
                print("No vault found. Enroll first.")
    return None

def enroller(image, THE_KEY):
    if image is None:
        print("Capture failed")
    else:
        points = get_landmarks(image)
        if points is None:
            print("No face detected")
            return False
        else:
            # Generating a 256 bit private key
            private_key = ec.generate_private_key(ec.SECP256K1()).private_numbers().private_value
            util.filewriter(str(private_key), 'priv_key')
            vault, h = lock(points, private_key, len(str(private_key)), THE_KEY)
            #Dumping the vault into a pickle file
            with open(os.path.join(path, "vault.pkl"), "wb") as f:
                pickle.dump((vault, h), f)
            print("Enrollment complete. Vault saved.")
            return True


if __name__ == "__main__":
    mode = input("Enter mode (enroll/verify): ").strip().lower()
    # For test case can be removed in production
    if input("Is this a test?(y/n)").strip().lower()=="y":
        path = input("enter file name")
        image = cv2.imread(path)
    else:
        image = capture_image()
    THE_KEY = evaluator.keyGiver(userName)
    if mode in ["enroll", "e"]:
        enroller(image, THE_KEY)
    elif mode in ["verify", "v"]:
        verifier(image, THE_KEY)
    else:
        print("Invalid mode.")