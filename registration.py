# registration.py (FINAL - FULLY CORRECTED)

import cv2
import os
import time
import pandas as pd
import tkinter as tk
from tkinter import messagebox, Toplevel, W, E
import tkinter.ttk as ttk # <-- CRITICAL FIX: Standard ttk import for Progressbar
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from encode_faces import create_encodings 
from PIL import Image, ImageTk
import threading 

# --- Configuration ---
DATA_PATH = "Data_Set"
DETAILS_FILE = "student_details.xlsx"
IMAGES_TO_CAPTURE = 5     
CAPTURE_INTERVAL = 1.0     
# ---------------------

if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

def show_loading_screen(master, style):
    """Creates a simple loading window while the camera initializes."""
    loading_win = Toplevel(master)
    loading_win.title("Loading...")
    loading_win.geometry("300x150")
    
    # Center the window
    master.update_idletasks()
    x = master.winfo_x() + (master.winfo_width() // 2) - (300 // 2)
    y = master.winfo_y() + (master.winfo_height() // 2) - (150 // 2)
    loading_win.geometry(f"+{x}+{y}")
    
    # Make the window modal and prevent user from closing it manually
    loading_win.transient(master) 
    loading_win.grab_set() 

    tk.Label(loading_win, text="Initializing Camera... Please wait.", 
             font=('Arial', 12, 'bold'), fg=style.colors.primary).pack(pady=30)
    
    # FIX: Use ttk.Progressbar (which is automatically styled)
    ttk.Progressbar(loading_win, orient=tk.HORIZONTAL, mode='indeterminate', length=200).pack(pady=10)
    
    return loading_win

class RegistrationWindow:
    def __init__(self, master, style):
        self.master = master
        self.style = style 
        master.title("Student Registration")
        master.geometry("550x420")
        master.resizable(True, False)
        
        master.grid_columnconfigure(1, weight=1)
        
        self.entries = {}
        self.fields = ["Ticket Number (ID)", "Full Name", "Department", "Section (A/B)"]
        
        # Title header
        tk.Label(master, text="STUDENT ENROLLMENT FORM", 
                 font=('Arial', 18, 'bold'), 
                 fg=self.style.colors.primary).grid(row=0, column=0, columnspan=2, pady=(15, 25))

        # 1. Create Input Form 
        for i, field in enumerate(self.fields):
            tk.Label(master, text=f"{field}:", font=('Arial', 10, 'bold')).grid(row=i+1, column=0, padx=15, pady=10, sticky='w')
            
            entry = tk.Entry(master, width=40, relief=tk.FLAT, borderwidth=2, font=('Arial', 11)) 
            entry.grid(row=i+1, column=1, padx=25, pady=10, sticky='ew')
            self.entries[field] = entry
            
        # 2. Add 'Next' Button 
        tk.Button(master, text="NEXT: CAPTURE IMAGES", command=self.process_details, 
               bg=self.style.colors.primary, fg='white', 
               font=('Arial', 11, 'bold'), width=40).grid(row=len(self.fields)+1, column=0, columnspan=2, pady=35, padx=25, sticky='ew')
        
    def process_details(self):
        """Validates input, saves details, and initiates image capture."""
        details = {field: self.entries[field].get().strip() for field in self.fields}
        
        if any(not value for value in details.values()):
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        # Create unique identifier and folder name logic
        student_id = details["Ticket Number (ID)"]
        name_clean = details["Full Name"].replace(" ", "_")
        dept_clean = details["Department"].replace(" ", "_")
        section_clean = details["Section (A/B)"].replace(" ", "_")
        
        self.folder_name = f"{student_id}_{name_clean}_{dept_clean}_{section_clean}"
        self.student_folder = os.path.join(DATA_PATH, self.folder_name)

        if os.path.exists(self.student_folder):
            messagebox.showerror("Error", f"Student ID {student_id} already exists. Check the ID.")
            return

        os.makedirs(self.student_folder)
        
        self.save_details_to_excel(details)
        self.capture_images_window()
        
    def save_details_to_excel(self, details):
        """Appends the student details to the main Excel sheet."""
        
        details_df = pd.DataFrame([details])

        existing_df = pd.DataFrame()
        if os.path.exists(DETAILS_FILE):
            try:
                existing_df = pd.read_excel(DETAILS_FILE, engine='openpyxl')
            except ValueError:
                 print(f"[WARN] Existing {DETAILS_FILE} is corrupted or empty. Creating new.")

        if not existing_df.empty:
            updated_df = pd.concat([existing_df, details_df], ignore_index=True)
        else:
            updated_df = details_df

        updated_df.to_excel(DETAILS_FILE, index=False, engine='openpyxl')
        print(f"[SUCCESS] Student details saved to {DETAILS_FILE}")

    def capture_images_window(self):
        """Shows loading screen, then initiates camera capture via thread."""
        
        self.loading_win = show_loading_screen(self.master, self.style)
        
        camera_thread = threading.Thread(target=self.initialize_camera_threaded)
        camera_thread.start()

    def initialize_camera_threaded(self):
        """Worker thread function to handle the slow camera initialization."""
        print("[INFO] Starting camera initialization in background...")
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            self.master.after(0, lambda: self.handle_camera_error(self.loading_win))
        else:
            self.master.after(0, lambda: self.start_video_stream(self.loading_win))

    def handle_camera_error(self, loading_win):
        """Called by the main thread upon camera error."""
        loading_win.destroy()
        self.master.deiconify() 
        messagebox.showerror("Camera Error", "Could not open webcam. Check connections or if another app is using it.")
    
    
    def start_video_stream(self, loading_win):
        """Opens the final video capture window once the camera is ready."""
        loading_win.destroy() 
        
        capture_win = Toplevel(self.master)
        capture_win.title("Face Capture - Enrollment")
        
        tk.Label(capture_win, text=f"Look at the Camera! Capturing {IMAGES_TO_CAPTURE} images...", 
              font=('Arial', 12, 'bold'), fg=self.style.colors.danger).pack(pady=10)
        
        self.camera_label = tk.Label(capture_win, relief=tk.SUNKEN) 
        self.camera_label.pack(padx=10, pady=10)

        self.image_count = 0
        self.start_time = time.time()
        
        self.update_camera_frame(capture_win)
        self.master.withdraw() 
        

    def update_camera_frame(self, capture_win):
        """Reads frame, saves image periodically, and updates GUI."""
        ret, frame = self.cap.read()
        
        if ret:
            # 1. Image Saving Logic
            current_time = time.time()
            
            if current_time - self.start_time >= CAPTURE_INTERVAL and self.image_count < IMAGES_TO_CAPTURE:
                image_filename = os.path.join(self.student_folder, f"{self.image_count+1}.jpg")
                
                cv2.imwrite(image_filename, frame) 
                self.image_count += 1
                self.start_time = current_time
                print(f"Captured image {self.image_count}/{IMAGES_TO_CAPTURE}")
                
            # Draw a progress indicator on the frame
            cv2.putText(frame, f"Capturing: {self.image_count}/{IMAGES_TO_CAPTURE}", (10, 30), 
                        cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 0), 2)

            # 2. Display live feed (convert OpenCV frame to Tkinter format)
            cv2_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(cv2_img, (320, 240)) 
            
            img_pil = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(image=img_pil)
            
            self.camera_label.imgtk = img_tk
            self.camera_label.configure(image=img_tk)

            # 3. Check for Finish Condition
            if self.image_count < IMAGES_TO_CAPTURE:
                self.master.after(10, lambda: self.update_camera_frame(capture_win))
            else:
                self.cap.release()
                self.finish_capture(capture_win)
        else:
            messagebox.showerror("Camera Error", "Failed to read from camera.")
            self.cap.release()
            capture_win.destroy()


    def finish_capture(self, capture_win):
        """Cleans up and shows the Finish button."""
        self.camera_label.destroy()
        
        tk.Label(capture_win, text="Capture Complete! Encoded data will be saved.", 
                 fg=self.style.colors.success, font=('Arial', 14, 'bold')).pack(pady=10)
        
        tk.Button(capture_win, text="FINISH & SAVE ENCODINGS", command=lambda: self.final_finish(capture_win), 
               bg=self.style.colors.info, fg='white', 
               font=('Arial', 11, 'bold')).pack(pady=20)
               
    def final_finish(self, capture_win):
        """Runs the encoding script and closes windows."""
        create_encodings() 
        capture_win.destroy()
        messagebox.showinfo("Success", f"{self.folder_name} registered and encoded successfully!")
        self.master.destroy()