import tkinter as tk
from tkinter import ttk, Label
import cv2
from PIL import Image, ImageTk
import ctypes
from ctypes import windll
from pygrabber.dshow_graph import FilterGraph
import sv_ttk

CONST_MIN_WIDTH = 800
CONST_MIN_HEIGHT = 600

# Function to capture video frames and update the Tkinter window
def update_frame():
    ret, frame = cap.read()
    if ret:
        width = lbl_video.winfo_width()
        height = lbl_video.winfo_height()

        # Get the default webcam resolution
        if cap.isOpened():
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        else:
            w, h = CONST_MIN_WIDTH, CONST_MIN_HEIGHT  # Fallback to default if webcam is not accessible

        # Video ratio
        aspect_ratio = w / h

        # Resize frame preserving the aspect ratio
        if width / height < aspect_ratio:
            new_width = width
            new_height = int(width / aspect_ratio)
        else:
            new_width = int(height * aspect_ratio)
            new_height = height

        # Ensure the new dimensions are valid
        if new_width > 0 and new_height > 0:
            frame = cv2.resize(frame, (new_width, new_height))
            # Convert the frame to RGB format
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convert the frame to an ImageTk object
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            # Update the label with the new frame
            lbl_video.imgtk = imgtk
            lbl_video.config(image=imgtk)
        else:
            print("Invalid dimensions for resizing, skipping frame update")

    # Call this function again after 10ms
    lbl_video.after(10, update_frame)

# Function to change the camera based on the selected option
def change_camera(*args):
    global cap
    cam_index = camera_names.index(variable.get())
    # Release the previous camera
    cap.release()
    # Open the new camera
    cap = cv2.VideoCapture(cam_index)

# Function to detect system mode
def is_dark_mode():
    try:
        # Check if the system is in dark mode
        reg_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize'
        reg_value = 'AppsUseLightTheme'
        value = ctypes.c_uint32()
        size = ctypes.sizeof(value)
        status = windll.advapi32.RegGetValueW(
            windll.HKEY_CURRENT_USER, reg_key, reg_value, 2, ctypes.byref(value), ctypes.byref(size))
        return value.value == 0  # 0 means dark mode, 1 means light mode
    except Exception as e:
        print(f"Error checking system mode: {e}")
        return False  # Fallback to default

# Function to set theme based on system mode
def set_theme():
    if is_dark_mode():
        sv_ttk.use_dark_theme()
    else:
        sv_ttk.use_light_theme()  # Define your light theme function if necessary

# Function to get the list of camera names
def get_camera_names():
    graph = FilterGraph()
    return graph.get_input_devices()

# Function to update the camera options in the dropdown
def update_camera_options():
    global camera_names
    new_camera_names = get_camera_names()
    if new_camera_names != camera_names:
        camera_names = new_camera_names
        menu = cam_option['menu']
        menu.delete(0, 'end')
        for name in camera_names:
            menu.add_command(label=name, command=tk._setit(variable, name))
        if variable.get() not in camera_names:
            variable.set(camera_names[0])
    root.after(1000, update_camera_options)

# Capture video from the default webcam (device 0)
cap = cv2.VideoCapture(0)

# Get the default webcam resolution
if cap.isOpened():
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) + 45
else:
    width, height = CONST_MIN_WIDTH, CONST_MIN_HEIGHT + 45  # Fallback to default if webcam is not accessible

# Create the main application window
root = tk.Tk()
root.title("Seeker")
root.geometry(f"{width}x{height}")
root.resizable(True, True)

# Set the minimum size of the window
root.minsize(width, height)

# Create a frame to hold the dropdown and button
frame_controls = ttk.Frame(root)
frame_controls.pack(fill=tk.X, pady=(10, 5))

# Create a Combobox to select the camera
variable = tk.StringVar(root)
camera_names = get_camera_names()
variable.set(camera_names[0])  # default camera

cam_option = ttk.Combobox(frame_controls, textvariable=variable, values=camera_names, state="readonly")
cam_option.pack(side=tk.LEFT, padx=5)

# Add padding to the text in the Combobox
style = ttk.Style()
style.configure('TCombobox', padding=(10, 0, 10, 0))  # Adjust padding as needed

# Create a button to toggle the theme
button = ttk.Button(frame_controls, text="Toggle theme", command=sv_ttk.toggle_theme)
button.pack(side=tk.LEFT, padx=5)

# Create a label to display the video frames
lbl_video = Label(root)
lbl_video.pack(fill=tk.BOTH, expand=True)

# Start updating the camera options
update_camera_options()

# Start updating the frames
update_frame()

# Set theme based on system mode
set_theme()

# Start the Tkinter event loop
root.mainloop()

# Release the webcam and close any OpenCV windows when done
cap.release()
cv2.destroyAllWindows()
