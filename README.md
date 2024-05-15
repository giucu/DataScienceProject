# DataScienceProject
Final mandatory assignment of group Possum 🦡
Code for evaluation of classifiers has been slightly modified to read in only image and mask paths instead of the image and mask themselves due to some variety in feature extraction methods. 
To run, mainly have to change file path of the correct diagnosis csv, folder with images, and folder with masks. For 'evaluate_classifers', this is at lines 28-30, 'train_classifiers' at lines 17-23, and 'process_images' the first lines below "Main Script" heading. Latest version of Python 3.11 is used, along with standard cv2, mathplotlib, ski-mage, numpy, and pandas libraries.
