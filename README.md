# 🎓 Face Attendance System

A modern, real-time facial recognition system built with Python, OpenCV, and Tkinter (using TtkBootstrap for an attractive UI) for managing student check-in and check-out attendance.

## ✨ Features

* **Real-time Registration:** Captures multiple images of a student for robust face encoding.
* **Modern GUI:** Attractive and responsive user interface using TtkBootstrap.
* **Multithreaded Camera:** Eliminates the typical camera initialization delay for a smooth user experience.
* **Strict Time Windows:** Enforces strict attendance logging (e.g., Check-in only between 9:30 AM and 10:00 AM).
* **Automatic Logging:** Records attendance (ID, Name, Date, Time, Status) into an Excel (`.xlsx`) report.
* **Multi-Face Detection:** Capable of logging multiple students simultaneously.

## 🛠️ Prerequisites

Before running the application, ensure you have Python (3.x recommended) installed, and install the necessary libraries.

```bash
# Recommended: Create and activate a virtual environment
# python -m venv venv
# venv\Scripts\activate

pip install opencv-python numpy pandas openpyxl pillow
pip install face-recognition dlib
pip install ttkbootstrap