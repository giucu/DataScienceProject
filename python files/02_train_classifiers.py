import os
import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GroupKFold
from sklearn.metrics import accuracy_score #example for measuring performance
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn import tree
import matplotlib.pyplot as plt

import pickle


#Location of csv with correct labels for training images
file_data = 'combgt.csv'
df = pd.read_csv(file_data)
label = np.array(df['melanoma'])

#Location of data extracted by feature for all training images
file_features = 'Compiled2.csv'

#we orignally had tried 10 features, but used only 4 in the end
#feature_names = ['Asymmetry','Blue_gray_granules','Depigmentation','Compactness','Roundness','Mean_Laplacian','Std_Dev_Laplacian','Sat SD', 'Val SD', 'Hue SD']
feature_names = ['Asymmetry','Blue_gray_granules','Depigmentation','Val SD']

# Loading the features
df_features = pd.read_csv(file_features)

x = np.array(df_features[feature_names])
y =  label == 1 
id = 'image_id'
patient_id = df[id]

num_folds = 5
group_kfold = GroupKFold(n_splits=num_folds)
group_kfold.get_n_splits(x, y, patient_id)
num_classifiers = len(classifiers)
   
acc_val = np.empty([num_folds,num_classifiers])

for i, (train_index, val_index) in enumerate(group_kfold.split(x, y, patient_id)):
    
    x_train = x[train_index,:]
    y_train = y[train_index]
    x_val = x[val_index,:]
    y_val = y[val_index]
    
    
    for j, clf in enumerate(classifiers): 
        
        #Train the classifier
        clf.fit(x_train,y_train)
    
        #Evaluate your metric of choice (accuracy is probably not the best choice)
        acc_val[i,j] = accuracy_score(y_val, clf.predict(x_val))
   
average_acc = np.mean(acc_val,axis=0) 

# original classifier :
# classifier = DecisionTreeClassifier(random_state=0)
# classifier.fit(x, y)

# Final classifier with optimal hyperparameter N
classifier = KNeighborsClassifier(n_neighbors = 2)

classifier = classifier.fit(x,y)

# Saving pickle / classifier
filename = 'groupP_classifier2.sav'
pickle.dump(classifier, open(filename, 'wb'))
