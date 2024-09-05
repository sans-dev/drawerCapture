"""
Module: drawer_box_cropper.py
Author: Sebastian Sander
This module contains the implementation of the DrawerBoxCropper class, which is used to process images and crop the drawer box from them. The class provides methods for selecting a region of interest (ROI) from an image, calculating the color mask from the ROI, cropping the drawer box from the image, and saving the cropped image.
Usage:
    python drawer_box_cropper.py --images_dir <path_to_images_dir> --output_dir <path_to_output_dir>
Example:
    python drawer_box_cropper.py --images_dir /path/to/images --output_dir /path/to/output

"""


import cv2
import numpy as np
from argparse import ArgumentParser
from pathlib import Path
from tqdm import tqdm

class DrawerBoxCropper:
    def __init__(self, images_dir: Path, output_dir: Path):
        self.images_dir = images_dir
        self.output_dir = output_dir

    def process(self):
        image_dirs = list(self.images_dir.glob('*.jpg'))
        if not image_dirs:
            print(f'No images found in {self.images_dir}')
            return
        self.output_dir.mkdir(parents=True, exist_ok=True)
        is_roi = False
        pbar = tqdm(image_dirs, desc='Processing images', unit='image')

        for image_dir in pbar:
            image = cv2.imread(image_dir.as_posix())
            if not is_roi:
                pbar.set_description(f'Processing {image_dir.name} - Select ROI')
                roi = self.get_roi(image)
                lbound, hbound = self.calc_color_mask_from_roi(image,roi)
                is_roi = True

            pbar.set_description(f'Processing {image_dir.name} - Apply mask')
            image_crop = self.crop_drawer_box(image, lbound, hbound)
            self.save_image(image_crop, image_dir.name)

        print('Done!')

    def crop_drawer_box(self, image : np.ndarray, lbound : np.ndarray, hbound : np.ndarray):
        """Crops the box from the image

        Args:
            image (numpy array): image to be processed
            lbound (lower bound): lower bound of the color mask
            hbound (upper bound): upper bound of the color mask

        Returns:
            numpy array: cropped image
        """    
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # apply mask
        mask = cv2.inRange(
            image_hsv, 
            lbound,
            hbound
        )
        # apply mask to original image
        image_masked = cv2.bitwise_and(image, image, mask=mask)

        image_gray = cv2.cvtColor(image_masked, cv2.COLOR_BGR2GRAY)
        image_bin_otsu = cv2.threshold(image_gray, 0, 255, cv2.THRESH_BINARY)[1]
        # find the sum of white pixels in each row and column
        sum_height = np.abs(np.sum(image_bin_otsu, axis=1))
        sum_width = np.abs(np.sum(image_bin_otsu, axis=0))
        im_height, im_width = image.shape[:2]
        eval_divison = 4 
        #find borders of the box in the image by finding the max sum of white pixels in the image
        y_l = np.argmax(
            sum_height[:int(im_height/eval_divison)])
        y_r = im_height - np.argmax(
            np.flip(sum_height)[:int(im_height/eval_divison)])
        x_l = np.argmax(
            sum_width[:int(im_width/eval_divison)])
        x_r = im_width - np.argmax(
            np.flip(sum_width)[:int(im_width/eval_divison)])
        image_crop = image[y_l:y_r, x_l:x_r]
        return image_crop

    def scale_image(self, image : np.ndarray):
        """Scales the image to fit the screen

        Args:
            image (numpy array): image to be processed

        Returns:
            numpy array: scaled image
        """    
        max_height = 800
        scale_factor = max_height / image.shape[0]
        return cv2.resize(image, None, fx=scale_factor, fy=scale_factor), scale_factor
    
    def get_roi(self, image : np.ndarray):
        """Selects a ROI from the image

        Args:
            image (numpy array): image to be processed

        Returns:
            numpy array: ROI
        """    
        image_scaled, scale_factor = self.scale_image(image)
        roi = cv2.selectROI('Select ROI containing the drawer frame',image_scaled)
        cv2.destroyAllWindows()
        roi = (np.array(roi) / scale_factor).astype(int)
        return roi
    
    def crop_roi(self, image : np.ndarray, roi : np.ndarray):
        """Crops the ROI from the image

        Args:
            image (numpy array): image to be processed
            roi (numpy array): ROI to be cropped

        Returns:
            numpy array: cropped image
        """    
        return image[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]]
        
    def calc_color_mask_from_roi(self, image : np.ndarray, roi : np.ndarray):
        """Calculates the color mask from a ROI selected by the user

        Args:
            image (numpy array): image to be processed

        Returns:
            tuple: lower and upper bounds of the color mask
        """    
        # read image and convert to HSV
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv_crop = self.crop_roi(image, roi) 

        # find min and max values for each channel
        h_min, s_min, v_min = hsv_crop.min(axis=0).min(axis=0)
        h_max, s_max, v_max = hsv_crop.max(axis=0).max(axis=0)

        # apply mask
        lbound, hbound = np.array((h_min, s_min, v_min)), np.array((h_max, s_max, v_max))
        return lbound, hbound

    def save_image(self, image : np.ndarray, image_name : str):
        """image save function

        Args:
            image (numpy array): image to be saved 
            output_dir (pathlib.Path): output directory
            image_name (str): image name
        """    
        cv2.imwrite(self.output_dir.joinpath(image_name).as_posix(), image)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--images_dir', type=Path, required=True, help='Path to the directory containing the images')
    parser.add_argument('--output_dir', type=Path, required=True, help='Path to the directory where the images will be saved')
    cropper = DrawerBoxCropper(**vars(parser.parse_args()))
    cropper.process()