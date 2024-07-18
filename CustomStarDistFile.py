from BaseModelInterface import BaseModel
from tkinter import filedialog, messagebox, ttk
import numpy as np
from glob import glob
from tifffile import imread
from tqdm import tqdm
from csbdeep.utils import normalize
from stardist.models import StarDist2D
from stardist.models import StarDist2D
import cv2


class CustomStarDist(BaseModel):
    # Constructor when the user passes through a pretrained models location in directory
    def __init__(self, model_name, base_directory, root, GUI):
        # Setting up the window 
        self.root = root
        # Initialize the model
        self.StarDistModel = StarDist2D(None, name=model_name, basedir=base_directory)

        self.GUI = GUI

        self.X = None

        
    def load_images(self,directory):
        '''Loads images into a list of arrays to be passed through the model'''

        print("Loading Images")
        messagebox.showinfo("Loading Images")
        # Read Images
        try:
            self.file_list = sorted(glob(f'{directory}/*.tif'))
            self.X = list(map(imread, self.file_list))
            if len(self.X) == 0:
                messagebox.showinfo("No Images", "No images found in the specified directory.")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read images: {e}")
            return
    
        if self.X[0].shape[0] == 3:
            self.adjust_image_channels()

        self.normalize_images()
        
        self.run_model()

    def adjust_image_channels(self):
        '''Moves color channel last, from (C, W, H) to (W, H, C)'''

        for i in range(len(self.X)):
            self.X[i] = np.moveaxis(self.X[i], 0, -1)

    def normalize_images(self):
        '''Normalizes the images before being passed throught the model'''

        self.n_channel = 1 if self.X[0].ndim == 2 else self.X[0].shape[-1]
        axis_norm = (0, 1)
        if self.n_channel > 1:
            print("Normalizing image channels %s." % ('jointly' if axis_norm is None or 2 in axis_norm else 'independently'))
        self.X = [normalize(x, 1, 99.8, axis=axis_norm) for x in tqdm(self.X)]


    def run_model(self):
        '''Calls segment_channels, then waits for user to 
        move onto the next image in the viewer'''

        # Create counter for analytics screen to keep track 
        # of what row in the table we are on
        self.img_count = 0
        # Create the Analytics Screen
        self.GUI.create_analytics_screen(self.file_list, self.n_channel, self)
        for img in self.X:
            # Index to be used by the GUI, image_count starts at 1
            self.img_count +=1    

            self.segment_channels(img)

            # Wait for the image viewer window to be closed before continuing
            self.root.wait_window(self.GUI.current_viewer_window)



    def segment_channels(self, img: np.ndarray):
        '''Creates a list of three channel label images output from the model'''

        image_list = []
        details_list = []
        img_shape = img.shape
        num_channels = img_shape[-1]

        for current_channel in range(num_channels):
            # Split the original multi channel image into each individual channel
            single_channel_img = np.zeros((img_shape[0],img_shape[1],3))
            label_colored = np.zeros((img_shape[0],img_shape[1],3))

            for i in range(num_channels):
                single_channel_img[:,:,i] = img[:,:,current_channel]

            labels, details = self.StarDistModel.predict_instances(single_channel_img,n_tiles = self.StarDistModel._guess_n_tiles(img))
            label_colored[:,:,current_channel] = labels
            image_list.append(label_colored)
            details_list.append(details)

        # Send the list of labels and the list of details for each channel to the GUI
        self.GUI.labels_view_screen(img, image_list, details_list)


    def count_colocalized_cells(self, electroporated: np.array, marker1: np.array, marker2: np.array):
        '''Counts the co-localization (overlap) of the electroporated cells with marker1,
        an again with marker 2 and then divides those numbers by the total number of electroporated cells'''

        # Convert each label image to a mask for use with OpenCV
        electroporated = np.ma.asarray(electroporated, dtype=np.uint8)
        marker1 = np.ma.asarray(marker1, dtype=np.uint8)
        marker2 = np.ma.asarray(marker2, dtype=np.uint8)

        electroporated = cv2.cvtColor(electroporated, cv2.COLOR_BGR2GRAY)
        marker1 = cv2.cvtColor(marker1, cv2.COLOR_BGR2GRAY)
        marker2 = cv2.cvtColor(marker2, cv2.COLOR_BGR2GRAY)

        # Find overlapping regions
        overlap_mask1 = cv2.bitwise_and(electroporated, marker1)
        overlap_mask2 = cv2.bitwise_and(electroporated, marker2)

        # Find contours in the overlapping regions
        colocalize1, _ = cv2.findContours(overlap_mask1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        colocalize2, _ = cv2.findContours(overlap_mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        return len(colocalize1), len(colocalize2)