# attendance_log.py (FINAL & CORRECTED LOGIC: Logs "---" outside valid window)

import face_recognition
import cv2
import numpy as np
import pickle
import pandas as pd
from datetime import datetime, time as time_function
import os
import time
from tkinter import messagebox 

# --- Configuration ---
ENCODINGS_FILE = "encodings.pkl"
ATTENDANCE_FILE = "attendance_report.xlsx"
TOLERANCE = 0.6 

# Time thresholds for Check-in/Check-out logic
CHECK_IN_START = time_function(9, 30, 0)
CHECK_IN_END = time_function(10, 0, 0)
CHECK_OUT_START = time_function(16, 30, 0) # 4:30 PM
CHECK_OUT_END = time_function(17, 30, 0)   # 5:30 PM
# ---------------------

def load_encodings():
    """Loads pre-calculated face encodings."""
    try:
        with open(ENCODINGS_FILE, "rb") as f:
            data = pickle.load(f)
            return data["encodings"], data["names"]
    except FileNotFoundError:
        messagebox.showerror("Error", "Encoding file not found. Run registration first.")
        return None, None
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load encodings: {e}")
        return None, None


def log_attendance(name):
    """Logs the attendance using the strict time windows defined in the configuration."""
    
    # 1. Parse Student Data (robust split fix)
    parts = name.split('_')
    
    if len(parts) < 4:
        student_id, student_name, dept, section = name, name, "N/A", "N/A"
    else:
        section = parts[-1] 
        dept = parts[-2]
        student_id = parts[0]
        name_parts = parts[1:-2] 
        student_name = " ".join(name_parts)
        
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    time_string = now.strftime("%H:%M:%S")
    day_string = now.strftime("%A") 

    # 2. STRICT ATTENDANCE STATUS LOGIC
    current_time = now.time()
    
    status_type = "---"
    attendance_status = "---"

    if CHECK_IN_START <= current_time <= CHECK_IN_END:
        attendance_status = "Present"
        status_type = "Check-in"
    elif CHECK_OUT_START <= current_time <= CHECK_OUT_END:
        attendance_status = "Present"
        status_type = "Check-out"
    
    # --- FIX APPLIED HERE ---
    # We NO LONGER return early. We proceed to log the entry with status "---".
    # ------------------------
        
    # 3. Prepare new record
    new_record = pd.DataFrame([{
        "Ticket Number": student_id,
        "Name": student_name,
        "Department": dept,
        "Section": section,
        "Date": date_string,
        "Day": day_string,
        "Time": time_string,
        "Status": attendance_status,
        "Type": status_type
    }])
    
    # 4. Check for duplicates 
    existing_df = pd.DataFrame()
    if os.path.exists(ATTENDANCE_FILE):
        try:
            existing_df = pd.read_excel(ATTENDANCE_FILE, engine='openpyxl')
        except ValueError:
             print(f"[WARN] Existing attendance file is corrupted or empty. Starting new.")
        except Exception:
             pass 

    # Check if this student already has this specific STATUS_TYPE logged today
    # Note: If status_type is "---", it will only check for other "---" entries, 
    # effectively preventing duplicates outside the official windows.
    is_duplicate = False
    if not existing_df.empty:
        is_duplicate = existing_df[
            (existing_df['Ticket Number'] == student_id) & 
            (existing_df['Date'] == date_string) &
            (existing_df['Type'] == status_type) 
        ].any().any()
        
    # 5. Write to Excel
    if not is_duplicate:
        if existing_df.empty:
            updated_df = new_record
        else:
            updated_df = pd.concat([existing_df, new_record], ignore_index=True)
            
        updated_df.to_excel(ATTENDANCE_FILE, index=False, engine='openpyxl')
        print(f"[LOG] {student_name} marked as {status_type}")
        return f"{student_name} - Status: {status_type}"
    else:
        return f"{student_name} already logged for {status_type} today."

def run_attendance_system():
    """Starts the webcam and real-time recognition loop."""
    Known_Faces_Encodings, Known_Faces_Names = load_encodings()
    
    if Known_Faces_Encodings is None or len(Known_Faces_Encodings) == 0:
        print("[ERROR] No face encodings loaded.")
        return

    video_capture = cv2.VideoCapture(0)
    
    if not video_capture.isOpened():
        print("[ERROR] Could not open webcam.")
        return

    print("--- Starting Real-time Attendance --- (Press 'q' to quit)")
    last_log_time = time.time()
    last_logged_name = ""
    log_message = "" 

    while True:
        ret, frame = video_capture.read()
        
        if not ret: break

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(Known_Faces_Encodings, face_encoding, TOLERANCE)
            name = "Unknown"

            face_distances = face_recognition.face_distance(Known_Faces_Encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index]:
                full_identifier = Known_Faces_Names[best_match_index]
                
                parts = full_identifier.split('_')
                if len(parts) >= 4:
                    display_name = " ".join(parts[1:-2])
                else:
                    display_name = full_identifier
                    
                name = display_name
                
                if full_identifier != last_logged_name or (time.time() - last_log_time) > 5:
                    log_message = log_attendance(full_identifier)
                    last_log_time = time.time()
                    last_logged_name = full_identifier
                
            face_names.append(name)

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255) 
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)

        if log_message:
            cv2.putText(frame, log_message, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)

        cv2.imshow('Attendance Scanner', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    print("Attendance System Closed.")