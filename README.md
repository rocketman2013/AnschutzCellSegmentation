# AnschutzCellSegmentation
<ins>App for segmenting and viewing the co-localization of cells in fluorescent images</ins>

This app takes in three channel flourescent images, where each channel shows the cells in a tissue slice containing a specific marker (Marker 1, Marker 2, Electropolated Channel). The goal of this app is to segment each channel, then calculate the ratio of marker 1 and marker 2 cells that co-localized with the electropolated cells *(ie. what cells in the tissue contain Marker X and are also electropolated)*. 

This is done by overlapping the model output masks of eack marker channel with the output mask of the electropolated channel, and dividing the number of overlapping cells by the total number of electropolated cells.



<ins>Image Viewer GUI:</ins>

<img width="511" alt="Screenshot 2024-07-18 at 4 36 43 PM" src="https://github.com/user-attachments/assets/9df11d9b-764d-4e81-b9b5-d090204f6741">



<ins>Image Analysis GUI:</ins>

<img width="763" alt="Screenshot 2024-07-18 at 4 37 45 PM" src="https://github.com/user-attachments/assets/f8459f68-2a18-47b1-8c74-1190bf11cdff">
