import tkinter as tk
from tkinter import Label
import cv2
from PIL import Image, ImageTk

# Function to capture video frames and update the Tkinter window
def update_frame():
    ret, frame = cap.read()
    if ret:
        # Convert the frame to RGB format
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Convert the frame to an ImageTk object
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        # Update the label with the new frame
        lbl_video.imgtk = imgtk
        lbl_video.config(image=imgtk)
    # Call this function again after 10ms
    lbl_video.after(10, update_frame)

# Capture video from the default webcam (device 0)
cap = cv2.VideoCapture(0)

# Get the default webcam resolution
if cap.isOpened():
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
else:
    width, height = 800, 600  # Fallback to default if webcam is not accessible

# Create the main application window
root = tk.Tk()
root.title("Seeker")
root.geometry(f"{width}x{height}")
root.configure(bg="white")
root.resizable(True, True)

# Set the minimum size of the window
root.minsize(width, height)

# Create a label to display the video frames
lbl_video = Label(root)
lbl_video.pack(fill=tk.BOTH, expand=True)

# Start updating the frames
update_frame()

# Start the Tkinter event loop
root.mainloop()

# Release the webcam and close any OpenCV windows when done
cap.release()
cv2.destroyAllWindows()
