import pickle #for loading your trained classifier

import extract_features as feat #our feature extraction
from os.path import exists
import os
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np


# The function that should classify new images. 
# The image and mask are the same size, and are already loaded using plt.imread
def classify(img_path, mask_path):
    
     im = plt.imread(img_path)
     img = np.float16(im)  
     mask = plt.imread(mask_path)
    
     #Extract features (the same ones that you used for training)
     x = feat.feature_extraction(img_path, mask_path)
     print(x)
         
     #Load the trained classifier
     classifier = pickle.load(open('groupP_classifier.sav', 'rb'))
    
     #Use it on this example to predict the label AND posterior probability
     pred_label = classifier.predict([x])
     pred_prob = classifier.predict_proba([x])
     
     #print('predicted label is ', pred_label)
     #print('predicted probability is ', pred_prob)
     return pred_label, pred_prob
 
    
# Change file path below

file_data = 'validation\ISIC-2017_Validation_Part3_GroundTruth.csv'
path_image = 'validation\images'
path_mask = 'validation\ISIC-2017_Validation_Part1_GroundTruth'
  
#Where we will store the features
file_features = 'evaluation_results.csv'

#Read meta-data into a Pandas dataframe
df = pd.read_csv(file_data)

# Extract image IDs and labels from the data. 
image_id = list(df['image_id'])
label = np.array(df['melanoma'])

num_images = len(image_id)

#Make array to store features
feature_names = ['True_Diagnosis', 'Diagnosis', 'Confidence','image ID']
num_features = len(feature_names)
features = np.zeros([num_images,num_features])  

# Remember to designate how many images you want to loop through, for now it's 10 for testing purposes.
for i in np.arange(0,10):
    
     # Define filenames related to this image
     file_image = path_image + os.sep + image_id[i] + ".jpg"
     maskid = image_id[i]
     maskid = maskid + "_segmentation.png"
     file_mask = path_mask + os.sep + maskid

     print(file_image)
     print(file_mask)
    
     if exists(file_image):
          x = classify(file_image, file_mask)
           
          if x[0][0]==False:
               features[i,1] = 0
          else:
               features[i,1] = 1
          '''Can also try (since original ground truth value are 0 / 1 instead of false / true, easier to compare):
          if x[0][0]=="True":
               features[i,1] = 1
          else:
               features[i,1] = 0
          '''
          features[i, 2] = x[1][0][0]
             
#Save the image_id used + features to a file   
df_features = pd.DataFrame(features, columns=feature_names)    
df_features["image ID"] = df["image_id"]
df_features["True_Diagnosis"] = df['melanoma']
df_features.to_csv(file_features, mode='a', header=not os.path.exists(file_features), index=False)
