import pickle #trained classifier
from extract_features2 import extract_features2 #importing feature extraction
from os.path import exists
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# main function to classify images, modified to take in img path instead of an already read image
def classify(img_path, mask_path):
    
     im = plt.imread(img_path)
     img = np.float16(im)  
     mask = plt.imread(mask_path)
    
     #Extract features
     x = extract_features2(img_path, mask_path)
     #Load the trained classifier
     classifier = pickle.load(open('groupP_classifier2.sav', 'rb'))
    
     pred_label = classifier.predict([x])
     pred_prob = classifier.predict_proba([x])
     
     return pred_label, pred_prob
 
    # location of validation testing data sets (csv, imgs, masks)
file_data = 'validation\ISIC-2017_Validation_Part3_GroundTruth.csv'
path_image = 'validation\images'
path_mask = 'validation\ISIC-2017_Validation_Part1_GroundTruth'
  
# storage of results
file_features = 'validation3.csv'

#Read meta-data
df = pd.read_csv(file_data)

# Extract image IDs and labels from the data. 
image_id = list(df['image_id'])
label = np.array(df['melanoma'])

num_images = len(image_id)

#Make array to store features
feature_names = ['True_Diagnosis', 'Diagnosis', 'Confidence','image ID']
num_features = len(feature_names)
features = np.zeros([num_images,num_features])  

#Loop through all images
for i in np.arange(0,150):
    
     # Define necessary file paths
     file_image = path_image + os.sep + image_id[i] + ".jpg"
     maskid = image_id[i]
     maskid = maskid + "_segmentation.png"
     file_mask = path_mask + os.sep + maskid

     print(file_image)
     print(file_mask)
    
     if exists(file_image):
          x = classify(file_image, file_mask)
           
          if x[0][0] is False: # based on results from classify function (returns 2D array with True/False for diagnosis)
               features[i, 1] = 0
          else:
               features[i, 1] = 1

          features[i, 2] = x[1][0][0]
             
#Save results 
df_features = pd.DataFrame(features, columns=feature_names)    
df_features["image ID"] = df["image_id"]
df_features["True_Diagnosis"] = df['melanoma']
df_features.to_csv(file_features, mode='a', header=not os.path.exists(file_features), index=False)
