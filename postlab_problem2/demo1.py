import tkinter as tk
from tkinter import filedialog

# Create a root window (hidden)
root = tk.Tk()
root.withdraw()  # Hide the root window

# Open file dialog
file_path = filedialog.askopenfilename(title="Select a text file",
                                       filetypes=[("Text files", "*.txt"), ("All files", "*.*")])

# Print the selected file path
if file_path:
    print("Selected file:", file_path)
else:
    print("No file selected.")
