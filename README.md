# DataScienceProject
Final mandatory assignment of group Possum 🦡
Code for evaluation of classifiers has been slightly modified to read in only image and mask paths instead of the image and mask themselves due to some variety in feature extraction methods. 

To run, you mainly have to change the file path of the correct diagnosis csv, folder with images, and folder with masks. 

### 01_process_images.py

Change file_data, path_image, path_mask, and n_imgs.

### 02_train_classifiers.py

Change file_data. 

### 03_evaluate_classifier.py

Change file_data, path_image, and path_mask.

### Version requirements

Latest version of Python 3.11 is used, along with standard cv2, mathplotlib, ski-mage, numpy, and pandas libraries. Make sure scikit-learn version is at least 1.4.2.

Note: Since our group used the external [ISIC Challenge 2017](https://challenge.isic-archive.com/data/#2017) data set, the groupP_masks only reflects masks for the first part of the project
