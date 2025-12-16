# main_app.py (FINAL & SYNCED CODE)

import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import Style
from ttkbootstrap.constants import * 
from registration import RegistrationWindow
from attendance_log import run_attendance_system

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.style = Style(theme='flatly') 
        
        self.title("Face Attendance System")
        self.geometry("450x280")
        self.resizable(False, False)
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self)
        main_frame.pack(pady=30, padx=20, fill="both", expand=True) 

        tk.Label(main_frame, text="ATTENDANCE CAPTURE SYSTEM", 
                 font=('Arial', 18, 'bold'), 
                 fg=self.style.colors.primary).pack(pady=10)
        
        tk.Button(main_frame, text="1. NEW STUDENT REGISTRATION", command=self.open_registration, 
                  width=30, height=2, 
                  bg=self.style.colors.warning, fg='white', 
                  font=('Arial', 10, 'bold')).pack(pady=15, fill=tk.X) 
                  
        tk.Button(main_frame, text="2. START ATTENDANCE SCAN", command=self.start_attendance, 
                  width=30, height=2, 
                  bg=self.style.colors.success, fg='white', 
                  font=('Arial', 10, 'bold')).pack(pady=10, fill=tk.X) 

    def open_registration(self):
        self.withdraw()
        reg_root = tk.Toplevel(self)
        reg_root.style = self.style 
        RegistrationWindow(reg_root, self.style) 
        reg_root.protocol("WM_DELETE_WINDOW", lambda: self.show_main_window(reg_root))
        
    def start_attendance(self):
        messagebox.showinfo("System Alert", "Starting Attendance Scanner. Press 'q' on the camera window to quit.")
        self.withdraw() 
        run_attendance_system()
        self.deiconify() 
        
    def show_main_window(self, window_to_destroy):
        window_to_destroy.destroy()
        self.deiconify() 

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()