# Import packages
import os
import cv2
import numpy as np
import tensorflow as tf
import sys
import easyocr
import re
from PIL import Image
from skimage import io
from skimage.transform import rotate
from skimage.color import rgb2gray
from deskew import determine_skew
from typing import Union
import math

aadhar_regex = r'^\d{4}\s\d{4}\s\d{4}$'
male = r'(?i)^Male\s*$'
dob = r'\d{2}/\d{2}/\d{4}'
name_regex = r'^[A-Za-z]+(?:\s[A-Za-z]+)+$'
pan_regex = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'



# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")

# Import utilites
from utils import label_map_util
from utils import visualization_utils as vis_util


# Initialize the OCR reader
reader = easyocr.Reader(['en'], gpu=False)  # This needs to run only once to load the model into memory


def rotate(
        image: np.ndarray, angle: float, background: Union[int, tuple[int, int, int]]
) -> np.ndarray:
    old_width, old_height = image.shape[:2]
    angle_radian = math.radians(angle)
    width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
    height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    rot_mat[1, 2] += (width - old_width) / 2
    rot_mat[0, 2] += (height - old_height) / 2
    return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))), borderValue=background)

image = cv2.imread('test_images/image.jpg')
grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
angle = determine_skew(grayscale)
rotated = rotate(image, angle, (0, 0, 0))
cv2.imwrite('image2.jpg', rotated)

# Perform OCR on the image
result = reader.readtext('image2.jpg')


for detection in result:
    text = detection[1]
    aadhar_match = re.search(aadhar_regex, text)
    pan_match = re.search(pan_regex, text)
    if aadhar_match:
        print("\n")
        print("AADHAR CARD")
        aadhar_no = aadhar_match.group()
        print("Aadhar No:", aadhar_no)
        for detection in result:
            text = detection[1]
            name_match = re.search(name_regex, text)
            if name_match and name_match.group() != "Government of India" and name_match.group() != "GOVERNMENT OF INDIA":
                name = name_match.group()
                print("Name:", name)

        for detection in result:
            text = detection[1]
            dob_match = re.search(dob, text)
            if dob_match:
                dob = dob_match.group()
                print("Date of Birth:", dob)


        for detection in result:
            text = detection[1]
            male_match = re.search(male, text)
            if male_match:
                print("Gender: Male")
    elif pan_match:
        print("\n")
        print("PAN CARD")
        pan_no = pan_match.group()
        print("Pan No:", pan_no)

print("\n")

# Delete the file
os.remove('image2.jpg')