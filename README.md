# 2D-image-marker-quantification
Method and Code for analysis of 2D cultures dopaminergic neurons used in Mohammed et al

An ImageJ macro that analyzes sets of fluorescence microscopy images.
The data must be in one parent directory with subdirectories containing images. The images must be one
per channel with matching names (a split image). The names of the image files must also have a specific
format, see notes of image naming below.

The macro first asks the user to choose the input, consisting of the directory two 
layers above images, and output directory, in which it will save the data acquired. 
The macro will ask the user to optionally submit a naming convention file, 
which is a table corresponding to what each well in the plate should be called in the 
rows of the output, as well as a threshold file which can be used to set up specific 
thresholds for each marker. Finally, the macro asks the user for the relevant markers 
and corresponding channel  in each image subfolder. 

The macro will loop through each subfolder at a time, detecting and measuring the 
colocalization and other relevant information for each nuclei detected. 


Notes on image names:
Either change your image names to fit the format we have included in the code or change line
XXXX to fit the naming convention of your images. 
Images must be named in the 
