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
import extract_features.py

#####################################################
# Feature score functions
#####################################################

# We created separate csv's for each of the implemented feature functions and pasted the relevant function code
# below when building each csv file (e.g. the following is for asymmetry)

# For converting from the extracted scores to csv, skip to the next section

def crop_im(image, mask):
    image[mask==0] = 0

    non_black_rows = []
    for i, row in enumerate(image):
        if np.any(row[:, :3] != [0, 0, 0]): 
            non_black_rows.append(i)
    rows = min(non_black_rows), max(non_black_rows)

    non_black_columns = []
    for j in range(image.shape[1]):  
        if np.any(image[:, j, :3] != [0, 0, 0]): 
            non_black_columns.append(j)
    cols = min(non_black_columns), max(non_black_columns)

    image = image[rows[0]:rows[1], cols[0]:cols[1],:]
    return(image)

#Asymmetry
def rotation_crop(image, mask):
    angles = [0, 22.5, 45, 67.5, 90, 112.5]
    scores = []
    images = []

    for a in angles:
        newim = image.copy()
        newma = mask.copy()
        newim = rotate(image, a)
        newma = rotate(mask, a)

        res = crop_im(newim, newma)
        images.append(res)
        symm = getsym(res)
        avgsym = (symm[0] + symm[1])/2
        scores.append(avgsym)
    return max(scores)

def getsym(image):
    h, w = image.shape[:2]
    hm = h // 2
    wm = w // 2

    if h % 2 == 0:  # Height is even
        upper = image[:hm, :]
        lower = image[hm:, :]
    else:  # Height is odd
        upper = image[:hm+1, :]
        lower = image[hm:, :]

    lower = np.flipud(lower)

    upper = (upper > 0).astype(np.uint8)
    lower = (lower > 0).astype(np.uint8)

    vintersection = np.logical_and(upper, lower)

    voverlap_percentage = (np.sum(vintersection) / np.sum(upper)) * 100
#######
    if w % 2 == 0:  # Width is even
        left = image[:, :wm]
        right = image[:, wm:]
    else:  # Width is odd
        left = image[:, :wm+1]
        right = image[:, wm:]
        
    left = np.fliplr(left)

    plt.imshow(right)
    plt.imshow(left)

    right = (right > 0).astype(np.uint8)
    left = (left > 0).astype(np.uint8)

    hintersection = np.logical_and(right, left)

    hoverlap_percentage = (np.sum(hintersection) / np.sum(right)) * 100
    #print("Percentage of v-overlap:", voverlap_percentage, "Percentage of h-overlap:", hoverlap_percentage)
    return (voverlap_percentage, hoverlap_percentage)


def segmentImage(input_img_path, mask_img_path, threshold=131, blockSize=15):

    img = cv2.imread(input_img_path)


    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


    binary_img = cv2.adaptiveThreshold(gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, threshold, blockSize)


    mask = cv2.imread(mask_img_path, cv2.IMREAD_GRAYSCALE)

    segmented_img = cv2.bitwise_and(binary_img, binary_img, mask=mask)

    return segmented_img

def calculateSegmentationScore(segmented_img, mask):

    area_mask = cv2.countNonZero(mask)
    area_segmented_img = cv2.countNonZero(segmented_img)
    score = (area_segmented_img / area_mask) * 100

    return score



#-------------------
# Main script
#-------------------


#File Paths of csv and image/mask folders
file_data = 'ISIC-2017_Training_Part3_GroundTruth.csv'
path_image = 'images'
path_mask = 'masks'
  
#Name of saved csv file
file_features = 'compiled2.csv'

#Read meta-data
df = pd.read_csv(file_data)

# Extract image IDs and labels from the data. 
image_id = list(df['image_id'])
label = np.array(df['melanoma'])

num_images = len(image_id)

#Feature and other csv headings array:
feature_names = ['Diagnosis','Asymmetry','Blue_gray_granules','Depigmentation','Compactness','Roundness','Mean_Laplacian','Std_Dev_Laplacian','Sat SD', 'Val SD', 'Hue SD','image ID']
num_features = len(feature_names)
features = np.zeros([num_images,num_features], dtype=np.float16)  

#main loop
for i in np.arange(0,2000):
    
    # Define filenames related to image
    file_image = path_image + os.sep + image_id[i] + ".jpg"
    maskid = image_id[i]
    maskid = maskid + "_segmentation.png"
    file_mask = path_mask + os.sep + maskid

    print(file_image)
    print(file_mask)
    
    if exists(file_image):
        print("does exist")
        
        # Read the image
        im = plt.imread(file_image)
        im = np.float16(im)  

        mask = plt.imread(file_mask)

        asymm = rotation_crop(im, mask)
        compact = 
        round = 
        # Storing variable in array
        features[i,1] = asymm

        if df.loc[i, "melanoma"]==1:
            features[i,0] = 1
        elif df.loc[i, "melanoma"]!= 1:
            features[i,0] = 0
       
        
#Saving array to df and exporting to csv
df_features = pd.DataFrame(features, columns=feature_names)    
df_features["image ID"] = df["image_id"]  
df_features.to_csv(file_features, mode='a', header=not os.path.exists(file_features), index=False)
