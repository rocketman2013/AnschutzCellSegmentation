import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageOps
import numpy as np


class SegmentAppGUI:
    def __init__(self, root, model_options, app):
        self.root = root
        self.root.title("Cell Segmentation App")

        self.model = None

        self.MODEL_OPTIONS = model_options

        self.App = app

        self.file_list = None


    def show_startup_screen(self):
        '''Startup Screen with train and run button
        NOTE: Train button is not currently supported'''

        welcome_label = tk.Label(self.root, text="Welcome to the Retinal Cell Detector!")
        welcome_label.grid(row=0,columnspan=2)

        model_menu = ttk.Combobox(self.root, values=self.MODEL_OPTIONS, state="readonly")
        model_menu.grid(row=1,columnspan=2)

        # Set the default menu option
        model_menu.current(0)


        train_button = tk.Button(self.root,text="Train New Model", command=self.model_train_screen)
        run_button = tk.Button(self.root,text="Run an Existing Model", command=self.model_run_screen)

        train_button.grid(row=3,column=0)
        run_button.grid(row=3,column=1)


    def model_train_screen(self):
        '''User clicks on train model button, needs to be implemented'''

        new_window = tk.Toplevel(self.root)
        new_window.title("Train a StarDist Model")

        label = tk.Label(new_window, text="Sorry, This feature is not currently available!")
        label.pack(pady=10)


    def model_run_screen(self):
        '''User clicks on run model button, promts user to select their 
        stardist model'''

        self.clear_current_screen()

        # Label for Model Path
        model_label = tk.Label(self.root, text="Select the folder in which your model files are contained")
        model_label.grid(row=0,pady=10)

        # Entry for Model Path
        self.model_path_entry = tk.Entry(self.root, width=50)
        self.model_path_entry.grid(row=1,column = 0,pady=10)

        button_explore = tk.Button(self.root, 
                                        text="Browse Files", 
                                        command=lambda: self.browse_path(self.model_path_entry))
        button_explore.grid(row=1,column=1,pady=10)


        # Send the model path to the load_model function in the CellSegmentationApp class in CellSegmentationApp.py
        model_load_button = tk.Button(self.root, text="Initialize Model", command =lambda: self.App.load_model(self.model_path_entry.get()))
        model_load_button.grid(row=2,pady=20)


    def image_input_screen(self):
        '''Once model is loaded, this screen promts them to select
        directory where images are stored'''

        self.clear_current_screen()

        # Label and Entry for Image Directory Path 
        image_dir_label = tk.Label(self.root, text="Select the folder where your images are located:")
        image_dir_label.grid(row=0,pady=10)

        image_dir_entry = tk.Entry(self.root, width=50)
        image_dir_entry.grid(row=1,pady=5)

        button_explore = tk.Button(self.root, 
                                        text="Browse Files", 
                                        command=lambda: self.browse_path(image_dir_entry))
        button_explore.grid(row=1,column=1,pady=10)

        # Segment Button 
        segment_button = tk.Button(self.root, text="Segment Images", command=lambda: self.App.send_images(image_dir_entry.get()))
        segment_button.grid(row=2,pady=20)


    ## HELPER FUNCTIONS FOR GENERAL LOADING SCREENS------
    def clear_current_screen(self):
        '''Clears all widgets from root'''

        for widget in self.root.winfo_children():
            widget.grid_forget()


    def browse_path(self,path_entry):
        '''Function to allow button to open file directory'''

        # Open a file dialog to select a folder
        model_path = filedialog.askdirectory()
        if model_path:
            # Insert the selected path into the model_path_entry
            path_entry.delete(0, tk.END)
            path_entry.insert(0, model_path)
    


    def create_analytics_screen(self, file_list, num_channel, model):
        '''This funciton is run once when the models run funciton is called.
        Here two global variables are set up referencing the file list of images 
        and the models instance'''

        self.model = model
        self.file_list = file_list
        self.num_channels = num_channel

        self.analytics_window = tk.Toplevel(self.root)
        self.analytics_window.title("Image Analysis")

        # List to keep track of row widgets
        self.row_widgets = []

        # Create the top row of the analytics screen
        if self.num_channels != 3:
            messagebox.showerror("Error", f"App Currently Only Supports 3 Channel Images")

        for col in range(4):
            b = tk.Entry(self.analytics_window, state='normal')
            b.grid(row = 0, column=col)
            if col == 0:
                b.insert(0, "File Name")
            elif col == 3:
                b.insert(0, "# cells in electroporated")
            else:
                b.insert(0, f"Ratio of electroporated with {col}")
            # Changing state so the user cannot edit contents of the table
            b.config(state='readonly')
  

    def try_update_analytics_screen(self):
        '''Tries to update the analytics screen, handles the case if the Toplevel window is closed.'''

        try:
            self.update_analytics_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update analytics screen: {e}")
            
            
    def update_analytics_screen(self):
        '''Adds a row to the analytics screen with either the number of cells in an image 
        if the image only has one channel, or the ratio of colocalizaiton with the 
        electroporated channel'''

        self.clear_current_row()  # Clear the current row before updating

        self.electropolated_idx = (int(self.electroporated_channel.get()) - 1)
        marker1_idx, marker2_idx = self.get_marker_idx(self.electropolated_idx)

        self.colocalize1, self.colocalize2 = self.model.count_colocalized_cells(
                                                        self.segmented_channels[self.electropolated_idx],
                                                        self.segmented_channels[marker1_idx],
                                                        self.segmented_channels[marker2_idx])
        
        self.analytics_screen_colocalize_counts()

    ## HELPER FUNCTIONS FOR ANALYTICS SCREEN-------

    def analytics_screen_colocalize_counts(self):
        '''Adds a row or updates a row with the ratio of overlap
        from the electerporolated channel'''

        # Getting the number of cells in the electerporated channel
        electropolated_details = self.details_list[self.electropolated_idx]
        num_electropolated = electropolated_details['points'].size

        # Storing the widgets in each row in case they need to be
        # updated (user selects different channel as enterporolated)
        row_widgets = []

        #Adding the items to the table
        for col in range(4):
            b = tk.Entry(self.analytics_window, state='normal')
            b.grid(row = self.model.img_count, column= col)
            row_widgets.append(b)
            if col == 0:
                image_name = os.path.basename(self.file_list[self.model.img_count - 1])
                b.insert(0, f"{image_name}")
            elif col == 1:
                coloc1 = self.colocalize1 / num_electropolated
                b.insert(0,np.round(coloc1,2))
            elif col == 2:
                coloc2 = self.colocalize2 / num_electropolated
                b.insert(0, np.round(coloc2,2))
            else:
                b.insert(0, num_electropolated)

            b.config(state='readonly')

            # Adding widgets from current row to the list
            self.row_widgets.append(row_widgets)


    def clear_current_row(self):
        '''Clears current row in analytics screen IF the row has been created, then
        deletes the rows widgets from the stored widget list'''

        if len(self.row_widgets) == self.model.img_count:  # Ensure there is a row to clear
            current_row_widgets = self.row_widgets[-1]
            for widget in current_row_widgets:
                widget.destroy()
            self.row_widgets.pop()


    def get_marker_idx(self, electropolated_idx):
        '''Marker 1 is the lowest channel out of three that is not the
        electoroporated channel, and Marker 2 is the largest channel'''

        marker1_idx, marker2_idx = -1, -1
        for channel in range(self.num_channels):
            if channel == electropolated_idx:
                pass
            elif marker1_idx == -1:
                marker1_idx = channel
            else:
                marker2_idx = channel
        
        assert marker1_idx != -1 and marker2_idx != -1

        return marker1_idx, marker2_idx
            


    def labels_view_screen(self, original_image, segmented_channels: list[np.ndarray], details):
        '''Creates an image view screen with options to select the electropolated channel,
        options to save the image and to go to the next image, and display the image itself 
        with the selected options applied'''

        #Creates a new screen to display said options and image
        new_window = tk.Toplevel(self.root)
        new_window.title("Segmented Image Viewer")

        #Getting the original image
        self.current_image = original_image
        self.segmented_channels = segmented_channels
        self.details_list = details
        self.selected_channels = [tk.BooleanVar(value=True) for _ in segmented_channels]

        self.current_viewer_window = new_window

        # Creating a frame inside the viewer to place the electropolated 
        # channel label and options
        electroporated_frame = tk.Frame(new_window)
        electroporated_frame.grid(row=0, column=0, columnspan=4)

        self.channel_options = []
        
        for channel in range(self.num_channels):
            self.channel_options.append((channel+1))

        # DropDown Menu for the electroporated_channel withing the frame
        electroporated_label = tk.Label(electroporated_frame, text="Select Electroporated Channel:")
        electroporated_label.grid(row=0, column=0) # ,padx=(10, 5), pady=10, sticky="w"

        self.electroporated_channel = ttk.Combobox(electroporated_frame, values=self.channel_options, state="readonly")
        self.electroporated_channel.grid(row=0, column=1) # , padx=(5, 10), pady=10, sticky="w"

        # Bind the <<ComboboxSelected>> event to the update_analytics_screen method
        self.electroporated_channel.bind("<<ComboboxSelected>>", lambda event: self.try_update_analytics_screen())

        # Set the default menu option
        if self.num_channels == 1:
            self.electroporated_channel.current(0)
        else: 
            self.electroporated_channel.current(2)


        image_frame = tk.Frame(new_window)
        image_frame.grid(row=1, column=0, columnspan=4)

        # Resize the original image for display
        display_size = (original_image.shape[1] // 2, original_image.shape[0] // 2)
        self.canvas = tk.Canvas(image_frame, width=display_size[0], height=display_size[1])
        self.canvas.grid(row=1, column=0, sticky="nsew")

        # Slider for alpha value adjustment
        self.alpha_slider = ttk.Scale(image_frame, 
                                      from_ = 0,
                                      to_ = 1,
                                      command= self.get_alpha,
                                      orient = 'vertical'
                                      )
        self.alpha_slider.grid(row=1, column=1, sticky='ns')
        self.alpha_slider.set(0.7)
        self.alpha_slider.bind("<ButtonRelease-1>", lambda event: self.get_alpha)

        # Force the canvas to update its size before displaying the image
        new_window.update_idletasks()

        self.update_image_display()
        self.try_update_analytics_screen()

        # Frame for checkboxes and button
        control_frame = tk.Frame(new_window)
        control_frame.grid(row=2, column=0, columnspan=4)

        # Checkboxes for each channel
        for i, var in enumerate(self.selected_channels):
            chk = tk.Checkbutton(control_frame, text=f"Channel {i+1}", variable=var, command=self.update_image_display)
            chk.grid(row=0, column=i)

        # Save button
        save_button = tk.Button(control_frame, text="Save Image", command=self.save_image)
        save_button.grid(row=1, column=0, columnspan=2)

        # Next Image button
        next_button = tk.Button(control_frame, text="Next Image", command=self.next_image)
        next_button.grid(row=1, column=2, columnspan=2)


    def update_image_display(self):
        '''Updates the image in the viewer when user toggles channels to be
        viewed'''

        # Clear the canvas before updating
        self.canvas.delete("all")

        # If no channels are selected, self.combined_image wil just be a 2D array with zeros (black screen)
        num_channels_selected = self.get_selected_channel_count()
        target_shape = self.current_image.shape

        # This creates the GRAYSCALE BACKGROUND image to be displayed behind the labels for selected channels
        if num_channels_selected == 0:
            # If no channels are selected, show a black screen
            self.combined_image = np.zeros((target_shape[0], target_shape[1], 3))
        else:
            # Combine selected channels into a single image
            self.combined_image = np.zeros((target_shape[0], target_shape[1], num_channels_selected))
            channel_idx = 0
            for i, var in enumerate(self.selected_channels):
                if var.get():
                    self.combined_image[:,:,channel_idx] = self.current_image[:,:,i]
                    channel_idx += 1
        
       
        # Convert the combined image to grayscale and make them three channels
        grayscale_image = np.mean(self.combined_image, axis=-1) if self.combined_image.ndim == 3 else self.combined_image
        grayscale_image = np.stack([grayscale_image] * 3, axis=-1)

        # Combine original image and selected segmented channels
        background_image = grayscale_image.copy()

        # Performig bitwise operation if there are multiple labels to show the overlap
        if num_channels_selected > 1:
            overlap_image = np.zeros((target_shape[0], target_shape[1], 3))
            initial_overlap = np.ones((target_shape[0], target_shape[1]))
    
        for i, var in enumerate(self.selected_channels):
            if var.get():
                segmented_channel = self.segmented_channels[i]

                # Performing bitwise operation to create overlap image
                if num_channels_selected > 1:
                    initial_overlap = (segmented_channel[:,:,i] > 0) & (initial_overlap > 0)

                background_image = background_image + (self.alpha * segmented_channel)
        
        if num_channels_selected > 1:
            # Creating a gold three channel image of the overlaps
            overlap_image[:,:,0] = initial_overlap
            overlap_image[:,:,1] = initial_overlap * 0.85

            background_image += overlap_image

        background_image = np.clip(background_image, 0, 1)
        # Changing the array into an image
        background_image = (background_image * 255).astype(np.uint8)

        # Creating an image of what is currently displayed 
        # in case the user wants to save it
        self.image_to_save = background_image

        background_image = Image.fromarray(background_image)

        # Get the current canvas size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Resize the image to fit the canvas
        background_image = background_image.resize((canvas_width, canvas_height), Image.LANCZOS)
        background_image_tk = ImageTk.PhotoImage(background_image)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=background_image_tk)
        self.canvas.image = background_image_tk


    ## HELPER FUNCTIONS FOR IMAGE VIEWER---------
    def get_alpha(self, e):
            try:
                self.alpha = self.alpha_slider.get()
            except:
                self.alpha = 0.7
    
            self.alpha = (1 - self.alpha) * 0.02
            self.update_image_display()
    
    def get_selected_channel_count(self):
        '''Gets the number of channels user has selected to view in viewer'''

        selected_count = sum(var.get() for var in self.selected_channels)
        return selected_count
    

    def next_image(self):
        '''Closes the current image viewer which promts the loop in 
        run funciton of the CustomStarDistFile.py to continue to next
        image'''

        # Close the current viewer window
        self.current_viewer_window.destroy()
        # Model will now the next image


    def save_image(self):
        '''Saves the current image the user sees in the viewer'''
        
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            Image.fromarray(self.image_to_save).save(file_path)
            messagebox.showinfo("Image Saved", f"Image saved to {file_path}")
