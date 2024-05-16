import numpy as np
import matplotlib.pyplot as plt
from skimage import morphology
import numpy as np
import matplotlib.pyplot as plt
import cv2
import skimage.io
from skimage.transform import rotate
from skimage.filters import threshold_otsu, gaussian, laplace
from skimage.measure import label, regionprops
from scipy.ndimage import binary_erosion
from numpy import pi
from skimage import transform
from skimage.color import rgb2gray, rgba2rgb
from skimage import io, color, morphology, measure

#-------------------
# Feauture functions
#------------------

# (for combination of feature functions, skip to next section)

def crop_im(image, mask):
    '''With image and corresponding ground truth mask as input, will apply the binary mask on the image to crop out
    lesion as well as extra rows and columns not containing pixels depicting the lesion.
    '''

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
    '''using 'getsym' function, calculated the symmetry score of the lesion at different angles
    and returns %symmetry of image
    '''

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
    m = max(scores)
    return (m)

def getsym(image):
    '''Calculates asymmetry of image given mask'''

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

def calculateSegmentationScore(file_im, file_mask):

    seg_im = segmentImage(file_im, file_mask)
    mask = plt.imread(file_mask)

    area_mask = cv2.countNonZero(mask)
    area_segmented_img = cv2.countNonZero(seg_im)
    score = (area_segmented_img / area_mask) * 100

    if score > 0.4:
        return (1)
    else:
        return(0)

def depigmentation(img, mask):

    croppedimage = crop_im(img, mask)

    grayscale_image = color.rgb2gray(croppedimage)
    thresholded_image = grayscale_image > 0.4

    binary_image = morphology.binary_closing(thresholded_image, morphology.disk(5))

    contours = measure.find_contours(binary_image, 0.5)

    max_area = 200
    filtered_blobs = []

    for contour in contours:
        area = len(contour)
        if area <= max_area and area>=40:
            filtered_blobs.append(contour)

    num_filtered_blobs = len(filtered_blobs)

    return num_filtered_blobs

def get_area(mask):
    '''
    Input a mask and get the area of the lesion, full area of the image, and %of image covered by lesion
    '''
#create a binary mask where pixels with values greater than 0 are set to 1 (True) and others to 0 (False)
    binary_mask = (mask > 0).astype(np.uint8)

#calculate the total area covered by the mask
    mask_area = np.sum(binary_mask)

#calculates the original area of the mask.
    original_area = np.prod(mask.shape)

#computes the percentage of area covered by the mask compared to the original area
    percentage_covered = (mask_area / original_area) * 100
    return mask_area

def get_perimeter(mask, border_width=1):
    '''
    Input a mask and get the perimeter
    '''

    smaller_mask = binary_erosion(mask, iterations=border_width)

    # Subtract the smaller mask from the original mask to get the border mask
    border_mask = mask - smaller_mask
    plt.imshow(border_mask)

    # Sum the pixels in the border mask to get the perimeter
    perimeter = np.sum(border_mask)

    return perimeter

def get_compactness(mask):
    area = get_area(mask)
    perim = get_perimeter(mask)
    c = perim*perim
    c /= (4*pi*area)
    return c

def get_roundness(mask):
    maxdim = 0
    sum = 0
    for i in range(8):

#Finding the maximum number of pixels in any column
        pixels_in_col = np.sum(mask, axis=0)
        max_pixels_in_col = np.max(pixels_in_col)
        if max_pixels_in_col > maxdim:
            maxdim = max_pixels_in_col
        sum += max_pixels_in_col
#Rotating the mask by 45 degrees for the next iteration
        m2 = transform.rotate(mask, 45)
    return round(((sum/8)/maxdim)*100,2)

def get_surface_texture(image):
    gray = rgb2gray(image)
    blurred = gaussian(gray, sigma=1)
    
    #apply Laplacian filter to the blurred image
    laplacian = laplace(blurred)
    mean, std_dev = laplacian.mean(), laplacian.std()
    return mean, std_dev

#Color variation
#From https://github.com/ludekcizinsky/itu-fyp/blob/main/coursework/fyp2021p03g13/scripts/all_scripts.py

from skimage.measure import regionprops
from skimage.segmentation import slic

def find_topbottom(mask):
    '''
    Function to get top / bottom boundaries of lesion using a binary mask.
    :mask: Binary image mask as numpy.array
    :return: top, bottom as int
    '''
    region_row_indices = np.where(np.sum(mask, axis = 1) > 0)[0]
    top, bottom = region_row_indices[0], region_row_indices[-1]
    return top, bottom


def find_leftright(mask):
    '''
    Function to get left / right boundaries of lesion using a binary mask.
    :mask: Binary image mask as numpy.array
    :return: left, right as int
    '''

    region_column_indices = np.where(np.sum(mask, axis = 0) > 0)[0]
    left, right = region_column_indices[0], region_column_indices[-1]
    return left, right



def lesionMaskCrop(image, mask):
    '''
    This function masks and crops an area of a color image corresponding to a binary mask of same dimension.

    :image: RGB image read as numpy.array
    :mask: Corresponding binary mask as numpy.array
    '''
    # Getting top/bottom and left/right boundries of lesion
    top, bottom = find_topbottom(mask)
    left, right = find_leftright(mask)

    # Masking out lesion in color image
    im_masked = image.copy()
    im_masked[mask==0] = 0 # color 0 = black

    # Cropping image using lesion boundaries
    im_crop = im_masked[top:bottom+1,left:right+1]

    return(im_crop)



def rgb_to_hsv(r, g, b):

    """
    Credit for the entire function goes to:
    https://www.w3resource.com/python-exercises/math/python-math-exercise-77.php
    """
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = (df/mx)*100
    v = mx*100
    return h, s, v

def getColorFeatures(image, mask):

    """
    TODO: Add rest of the description

    This function computes the color brightness variations of an image, quantified as the IQR. This method
    uses SLIC segmentation to select superpixels for grathering average regional color intensities.
    These averages are converted to HSV to measure the spread of brightness ('Value') across all regions.

    :image: RGB image read as numpy.array
    :mask: Corresponding binary mask as numpy.array
    :return: list with extracted features
    """

    # Mask and crop image to only contain lesion
    im_lesion = lesionMaskCrop(image, mask)

    # Get SLIC boundaries
    segments = slic(im_lesion, n_segments=250, compactness=50, sigma=1, start_label=1)

    # Fetch RegionProps - this includes min/mean/max values for color intensity
    regions = regionprops(segments, intensity_image=im_lesion)

    # Access mean color intensity for each region
    mean_intensity = [r.mean_intensity for r in regions]

    # Get only segments with color in them
    color_intensity = []
    for mean in mean_intensity:
        if sum(mean) != 0:
            color_intensity.append(mean)

    # Convert RGB color means to HSV
    color_mean_hsv = [rgb_to_hsv(col_int[0], col_int[1], col_int[2]) for col_int in color_intensity]

    # Extract values for each channel
    color_mean_hue = [hsv[0] for hsv in color_mean_hsv]
    color_mean_satur = [hsv[1] for hsv in color_mean_hsv]
    color_mean_value = [hsv[2] for hsv in color_mean_hsv]

    # Compute different features based on the above values
    # * Compute SD for hue
    hue_sd = np.std(np.array(color_mean_hue))

    # * Compute SD for satur
    satur_sd = np.std(np.array(color_mean_satur))

    # * Compute SD for value
    value_sd = np.std(np.array(color_mean_value))

    if value_sd > 19.44089411041169: # binary output from the val SD
        return(1)
    else:
        return(0)


########################################################################
# FEATURE EXTRACTION FUNCTION
########################################################################

def feature_extraction(image_path, mask_path):

    im = plt.imread(image_path)
    im = np.float16(im)  
    im /= 255
    mask = plt.imread(mask_path)

    ## feature 1
    asymmetry = rotation_crop(im, mask)

    ## feature 2
    depig = depigmentation(im, mask)

    ## feature 3
    Blue_gray_granules = calculateSegmentationScore(image_path, mask_path)

    ## feature 4
    Val = getColorFeatures(im, mask)

    return np.array([asymmetry, depig, Blue_gray_granules,  Val], dtype=np.float16)
