# encode_faces.py

import face_recognition
import os
import pickle
import time

DATA_PATH = "Data_Set"
ENCODINGS_FILE = "encodings.pkl"

def create_encodings():
    print("--- Starting Face Encoding Process ---")
    start_time = time.time()
    
    Known_Faces_Encodings = []
    Known_Faces_Names = []
    
    # Loop through every folder (each student)
    for name in os.listdir(DATA_PATH):
        name_path = os.path.join(DATA_PATH, name)
        if os.path.isdir(name_path):
            print(f"Processing: {name}...")
            
            # Loop through every image file for the current student
            for filename in os.listdir(name_path):
                if filename.endswith(('.jpg', '.jpeg', '.png')):
                    filepath = os.path.join(name_path, filename)
                    
                    try:
                        image = face_recognition.load_image_file(filepath)
                        # Find the face location
                        face_locations = face_recognition.face_locations(image)
                        
                        if face_locations:
                            # Calculate the 128-dimension encoding
                            encoding = face_recognition.face_encodings(image, face_locations)[0]
                            
                            Known_Faces_Encodings.append(encoding)
                            # Store the folder name (e.g., '1001_Alex_CS_A') as the identifier
                            Known_Faces_Names.append(name) 
                        else:
                            # print(f"  [Warning] No face found in {filename}")
                            pass
                            
                    except Exception as e:
                        print(f"  [Error] Could not process {filename}: {e}")

    # Save the encodings and names to a pickle file
    data = {"encodings": Known_Faces_Encodings, "names": Known_Faces_Names}
    with open(ENCODINGS_FILE, "wb") as f:
        f.write(pickle.dumps(data))

    end_time = time.time()
    print("\n[SUCCESS] Encoding complete!")
    print(f"Total encoded faces: {len(Known_Faces_Encodings)}")
    print(f"Time taken: {round(end_time - start_time, 2)} seconds")
    
if __name__ == '__main__':
    create_encodings()