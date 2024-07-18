import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from glob import glob
from tifffile import imread
from CustomStarDistFile import CustomStarDist
from AppGUI import SegmentAppGUI


class CellSegmentationApp:
    def __init__(self, root):
        
        # Initialize model placeholder
        self.MODEL_OPTIONS = [
            "Custom StarDist Model"
        ]

        self.model = None
        self.model_path = None
        self.image_path = None

        self.GUI = SegmentAppGUI(root, self.MODEL_OPTIONS, self)
        self.GUI.show_startup_screen()


    def load_model(self, model_path):
        '''Send the required information to the constructor of the
        Stardist Model File'''

        # Get the model path from the entry
        base_directory = os.path.dirname(model_path)
        model_name = os.path.basename(model_path)
        if not model_path:
            messagebox.showerror("Error", "Please enter a directory path.")
            return
        if not model_name:
            messagebox.showerror("Error", "Please enter the name of your model")

        # Initialize the model and save a reference for it 
        try:
            self.model = CustomStarDist(model_name, base_directory, root, self.GUI)
            messagebox.showinfo("Success", "Model initialized successfully!")
            self.GUI.image_input_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to Initialize Model: {e}")
            return
        

    def send_images(self,directory):
        '''Send the images to the model, where it will then segment them
        and communicate that with the APPGUI'''

        # Get the directory path from the entry
        if not directory:
            messagebox.showerror("Error", "Please enter a directory path.")
            return

        # Read and process images
        print("Sending Images")
        self.model.load_images(directory)
        

if __name__ == "__main__":
    root = tk.Tk()
    app = CellSegmentationApp(root)
    root.mainloop()