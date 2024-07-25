# Cell Segmentation App
Authors & Contributors: Henry Lewinsohn

StarDist Model Page: https://github.com/stardist/stardist

## Overview
**View and analyze medical images with pathology-specific deep learning models**

This project provides the framework for an image viewer and image analysis window for you to use to visualize and analyze the predictions of your deep learning models on multi-channel microscopy images. Feel free to customize this code to support your specific needs, whether that be a different analysis method for your research, or adding a new type of model to app.


<ins>Workflow:</ins>



<img width="799" alt="Screenshot 2024-07-24 at 10 52 08 AM" src="https://github.com/user-attachments/assets/14c078ba-d458-4d78-8f3b-2f1255c7a28d">



<ins>Currently supported functionality:</ins>
  - View and save your models predictions for multi-channel images
  - Adjustable alpha widget in the image viewer (adjust the opacity of the models prediction)
  - Total cell count in an image/channel
  - Analysis of co-localized cells in multi-channel images

<ins>ToDo:</ins>
  - Impliment the "train a model" functionality for StarDist model (with your own images and ground truths)
  - ROI selection box for loaded images (send the selected region throught the specified model instead of the whole image)
  - Option to view the outline of cell predictions in order to better determine models performance for densely packed cells


<ins>Image Viewer GUI:</ins>


<img width="511" alt="Screenshot 2024-07-18 at 4 36 43 PM" src="https://github.com/user-attachments/assets/9df11d9b-764d-4e81-b9b5-d090204f6741">


<ins>Image Analysis GUI:</ins>

<img width="763" alt="Screenshot 2024-07-18 at 4 37 45 PM" src="https://github.com/user-attachments/assets/f8459f68-2a18-47b1-8c74-1190bf11cdff">


<ins>Example of the capabilities of the current app:</ins>

The app takes in three channel flourescent images, where each channel shows the cells in a tissue slice containing a specific marker (Marker 1, Marker 2, Electropolated Channel). The goal of this app is to segment each channel, then calculate the ratio of marker 1 and marker 2 cells that co-localized with the electropolated cells *(ie. what cells in the tissue contain Marker X and are also electropolated)*. 

This is done by overlapping the model output masks of eack marker channel with the output mask of the electropolated channel, and dividing the number of overlapping cells by the total number of electropolated cells.
