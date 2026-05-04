import cv2
from cryptography.hazmat.primitives.asymmetric import ec
import dlib
import random
from itertools import combinations
from collections import Counter
import pickle
import hashlib
import utilities as util
import evaluator
import os
import bz2
import requests


path = os.path.dirname(__file__)

# Note: Install dlib and opencv: pip install dlib opencv-python
# Download shape_predictor_68_face_landmarks.dat from http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
# Unzip and place in the same directory as this file (bio_final/)

PREDICTOR_PATH = os.path.join(os.path.dirname(__file__), "shape_predictor_68_face_landmarks.dat")
PRIME = 2**521 - 1  # Large prime
QUANTIZE = 5  # Quantization step for tolerance
userName = "john cena"

def get_landmarks(image):
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(PREDICTOR_PATH)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Improve contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)

    # Try multiple orientations for robustness
    orientations = [
        ("Original", gray),
        ("Flip H", cv2.flip(gray, 1)),
        ("Rotate 90 CW", cv2.rotate(gray, cv2.ROTATE_90_CLOCKWISE)),
        ("Rotate 90 CCW", cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE)),
        ("Rotate 180", cv2.rotate(gray, cv2.ROTATE_180))
    ]

    faces = None
    for label, img in orientations:
        faces = detector(img, 2)  # Upsample 2 times for better detection
        if len(faces) > 0:
            print(f"DEBUG: Face detected in {label} orientation.")
            gray = img  # Use the successful orientation
            break

    if not faces or len(faces) == 0:
        # Save debug image
        cv2.imwrite(os.path.join(path, "debug_no_face_detected.png"), image)
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

NUM_SECTIONS = 4  # Number of cross-verification sections
MATCH_THRESHOLD = 2  # Minimum sections that must agree on the same key

def eval_poly(coeffs, p, key):
    result = coeffs[0]
    result = result * (p % key)
    return result

def lock(points, secret, key_len, key):
    """Lock the secret into a fuzzy vault.
    Every genuine point encodes the FULL secret. Points are sorted in
    increasing order and assigned to 6 sections via round-robin for
    cross-verification grouping.
    Each vault entry is (x, y, section_index).
    Returns (vault, secret_hash).
    """
    max_point = max(points)
    min_point = min(points)
    coeffs = [secret]

    # Sort points and assign sections via round-robin
    sorted_points = sorted(points)

    # Each genuine point encodes the full secret
    genuine_points = []
    for i, p in enumerate(sorted_points):
        section = i % NUM_SECTIONS
        y = eval_poly(coeffs, p, key)
        genuine_points.append((p, y, section))

    # Generate chaff points (indistinguishable from genuine)
    chaff_count = len(points) * 5
    chaff_points = []
    used_x = set(points)
    while len(chaff_points) < chaff_count:
        x = random.randint(min_point, max_point)
        if x not in used_x:
            used_x.add(x)
            section = random.randint(0, NUM_SECTIONS - 1)
            y = random.randint(int('1' + '0' * (key_len - 1)), int('9' * key_len))
            true_y = eval_poly(coeffs, x, key)
            if y != true_y:
                chaff_points.append((x, y, section))

    vault = genuine_points + chaff_points
    random.shuffle(vault)
    return vault, hashlib.sha256(str(secret).encode()).hexdigest()

def unlock(points, vault, key):
    """Unlock the vault by matching facial landmark points.
    Each matched genuine point independently recovers the full key.
    Points are grouped by section (0-5). If any 2 sections' majority-vote
    keys agree, that key is returned as verified.
    """
    # Find candidate points that match the unlock face's landmarks
    candidate_points = []
    for x in points:
        for vx, vy, vs in vault:
            if vx == x:
                candidate_points.append((vx, vy, vs))
                break

    if not candidate_points:
        print("WHO THE HELL ARE YOU??")
        return None

    # Decode a candidate key from each matched point, group by section
    section_keys = {}
    for vx, vy, vs in candidate_points:
        try:
            mod_val = vx % key
            if mod_val == 0:
                continue
            candidate_key = vy // mod_val
            if vs not in section_keys:
                section_keys[vs] = []
            section_keys[vs].append(candidate_key)
        except Exception:
            continue

    # For each section, find the most common key (majority vote)
    section_best = {}
    for section, keys in section_keys.items():
        counts = Counter(keys)
        best_key, best_count = counts.most_common(1)[0]
        section_best[section] = best_key
        print(f"Section {section}: best key from {best_count} point(s)")

    # Cross-verify: find a key that at least MATCH_THRESHOLD sections agree on
    key_votes = Counter(section_best.values())
    for candidate_key, vote_count in key_votes.most_common():
        if vote_count >= MATCH_THRESHOLD:
            agreeing = [s for s, k in section_best.items() if k == candidate_key]
            print(f"Sections {agreeing} agree — key verified! ({vote_count}/{MATCH_THRESHOLD} threshold)")
            return candidate_key

    print(f"No key reached {MATCH_THRESHOLD}-section agreement.")
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
        return None
    points = get_landmarks(image)
    if points is None:
        print("No face detected")
        return None
    try:
        vault_path = os.path.join(path, "vault.pkl")
        with open(vault_path, "rb") as f:
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
                print("Verification failed.", recovered_secret)
        else:
            print("Verification failed.")
    except FileNotFoundError:
        print("No vault found. Enroll first.")
    return None

def enroller(image, THE_KEY):
    if image is None:
        print("Capture failed")
        return False
    points = get_landmarks(image)
    if points is None:
        print("No face detected")
        return False
    # Generating a 256-bit private key
    private_key = ec.generate_private_key(ec.SECP256K1()).private_numbers().private_value
    util.filewriter(str(private_key), 'priv_key')
    vault, h = lock(points, private_key, len(str(private_key)), THE_KEY)
    vault_path = os.path.join(path, "vault.pkl")
    with open(vault_path, "wb") as f:
        pickle.dump((vault, h), f)
    print("Enrollment complete. Vault saved (6-section cross-verification).")
    return True


def download_landmarks():
    file_name = "shape_predictor_68_face_landmarks.dat"
    bz2_name = file_name + ".bz2"
    url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"

    if not os.path.exists(file_name):
        print("Downloading face landmarks model (this may take a minute)...")
        with requests.get(url, stream=True) as r, open(bz2_name, 'wb') as f:  # ✅ open file once
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)  # ✅ append each chunk to the same open file

        print("Decompressing file...")
        with bz2.BZ2File(bz2_name) as fr, open(file_name, 'wb') as fw:
            fw.write(fr.read())

        os.remove(bz2_name)
        print("Done!")

if __name__ == "__main__":
    mode = input("Enter mode (enroll/verify): ").strip().lower()
    if input("Is this a test?(y/n)").strip().lower() == "y":
        img_path = input("Enter file name: ")
        image = cv2.imread(img_path)
    else:
        image = capture_image()
    THE_KEY = evaluator.keyGiver(userName)
    if mode in ["enroll", "e"]:
        enroller(image, THE_KEY)
    elif mode in ["verify", "v"]:
        verifier(image, THE_KEY)
    else:
        print("Invalid mode.")
