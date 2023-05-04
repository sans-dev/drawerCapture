import unittest
import cv2
import numpy as np
from pathlib import Path

from src.processors.drawer_box_cropper import DrawerBoxCropper
from src.utils.plotting import show_image

class TestDrawerBoxCropper(unittest.TestCase):
    def setUp(self):
        self.images_dir = Path('data/images/test/input')
        self.output_dir = Path('data/images/test/output')
        self.cropper = DrawerBoxCropper(self.images_dir, self.output_dir)
        self.generate_mockup_images()

    def tearDown(self):
        image_dirs = self.output_dir.glob('*.jpg')
        for image_dir in image_dirs:
            image_dir.unlink()

    def generate_mockup_images(self):
        black = (0, 0, 0)
        image = np.ones((200, 200, 3), np.uint8)*255
        image[50:150, 50:150] = black
        image[0:10, 0:200] = black
        image[190:200, 0:200] = black
        image[0:200, 0:10] = black
        image[0:200, 190:200] = black
        for i in range(10):
            image_name = f'IMG_20201019_151950_{i}.jpg'
            cv2.imwrite(self.images_dir.joinpath(image_name).as_posix(), image)

    def test_calc_gradiends(self):
        image = cv2.imread(self.images_dir.joinpath('IMG_20201019_151950_1.jpg').as_posix())
        sobelx, sobely = self.cropper.calc_gradiends(image)
        msg = f'Expected sobelx: {sobelx} - Actual sobelx: {sobelx}'
        self.assertTrue((sobelx==sobelx).all(),msg=msg)
        msg = f'Expected sobely: {sobely} - Actual sobely: {sobely}'
        self.assertTrue((sobely==sobely).all(),msg=msg)

    def test_get_roi(self):
        image = cv2.imread(self.images_dir.joinpath('IMG_20201019_151950_1.jpg').as_posix())
        roi = self.cropper.get_roi(image)
        msg = f'Expected roi: {roi} - Actual roi: {roi}'
        self.assertTrue((roi==roi).all(),msg=msg)

    def test_calc_color_mask_from_roi(self):
        image = cv2.imread(self.images_dir.joinpath('IMG_20201019_151950_1.jpg').as_posix())
        roi = self.cropper.get_roi(image)
        lbound, hbound = self.cropper.calc_color_mask_from_roi(image,roi)
        msg = f'Expected lower bound: [0, 0, 255] - Actual lower bound: {lbound}'
        self.assertTrue((lbound==np.array([0, 0, 255])).all(),msg=msg)
        msg = f'Expected upper bound: [0, 0, 255] - Actual upper bound: {hbound}'
        self.assertTrue((hbound==np.array([0, 0, 255])).all(),msg=msg)
    
    def test_crop_drawer_box(self):
        image = cv2.imread(self.images_dir.joinpath('IMG_20201019_151950_1.jpg').as_posix())
        lbound = np.array([0, 0, 255])
        hbound = np.array([0, 0, 255])
        image_crop = self.cropper.crop_drawer_box(image, lbound, hbound)
        expected_shape = (190, 190, 3)
        msg = f'Expected shape: {expected_shape} - Actual shape: {image_crop.shape}'
        self.assertTrue(image_crop.shape[0] > 100, msg=msg)
        self.assertTrue(image_crop.shape[1] > 100, msg=msg)
        self.assertTrue(image_crop.shape[2] == 3, msg=msg)
    
    def test_save_image(self):
        image_name = 'IMG_20201019_151950_1.jpg'
        image = cv2.imread(self.images_dir.joinpath(image_name).as_posix())
        self.cropper.save_image(image, image_name)
        self.assertTrue(self.output_dir.joinpath(image_name).exists())
    
    def test_process(self):
        self.cropper.process()
        image_dirs = self.output_dir.glob('*.jpg')
        self.assertEqual(len(list(image_dirs)), 10)

if __name__ == '__main__':
    unittest.main()