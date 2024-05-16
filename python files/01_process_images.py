import os
from os.path import exists
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2
import skimage.io
import numpy as np
from skimage.transform import rotate
from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops
import matplotlib.pyplot as plt
from scipy.ndimage import binary_erosion
import extract_features as feat

#-------------------
# Main script
#-------------------


#File Paths of csv and image/mask folders
file_data = 'ISIC-2017_Training_Part3_GroundTruth.csv'
path_image = 'images'
path_mask = 'masks'

n_imgs = 10 #change to fit your data set size

#Name of saved csv file
file_features = 'compiled_features.csv'

#Read meta-data
df = pd.read_csv(file_data)

# Extract image IDs and labels from the data. 
image_id = list(df['image_id'])
label = np.array(df['melanoma'])

num_images = len(image_id)

#Feature and other csv headings array:
feature_names = ['Diagnosis','Asymmetry','Blue_gray_granules','Depigmentation','Val SD','image ID']
num_features = len(feature_names)
features = np.zeros([n_imgs,num_features], dtype=np.float16)

#main loop
for i in np.arange(0,n_imgs):
    
    # Define filenames related to image
    file_image = path_image + os.sep + image_id[i] + ".jpg"
    maskid = image_id[i]
    maskid = maskid + "_segmentation.png"
    file_mask = path_mask + os.sep + maskid
    
    if exists(file_image):
        
        # Read the image
        im = plt.imread(file_image)
        im = np.float16(im)  

        mask = plt.imread(file_mask)

        asymm = feat.rotation_crop(im, mask)
        bgb = feat.calculateSegmentationScore(file_image, file_mask)
        depig = feat.depigmentation(im, mask)
        sd_val = feat.getColorFeatures(im, mask)

        # Storing variable in array
        features[i,1] = asymm
        features[i,2] = bgb
        features[i,3] = depig
        features[i,4] = sd_val


        if df.loc[i, "melanoma"]==1:
            features[i,0] = 1
        elif df.loc[i, "melanoma"]!= 1:
            features[i,0] = 0
       
        
#Saving array to df and exporting to csv
df_features = pd.DataFrame(features, columns=feature_names)    
df_features["image ID"] = df["image_id"]  
df_features.to_csv(file_features, mode='a', header=not os.path.exists(file_features), index=False)
