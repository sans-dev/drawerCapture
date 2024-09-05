import logging
import logging.config

import numpy as np
import cv2

logging.config.fileConfig('configs/logging/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class AdaptiveHE:
    def __init__(self, emitter, clip_limit : int = 2, tile_size : tuple = (8,8)):
        """
        Initializes an instance of the AdaptiveHE class.

        Args:
        - clip_limit (int): Threshold for contrast limiting. Default is 2.
        - tile_size (tuple): Size of the tiles for contrast limiting. Default is (8,8).
        """
        super().__init__()
        self.clip_limit = clip_limit
        self.tile_size = tile_size
        self.emitter = emitter

    def process(self, image : np.ndarray) -> np.ndarray:
        """
        Applies contrast limited adaptive histogram equalization to the input image.

        Args:
        - image (np.ndarray): Input image to be processed.

        Returns:
        - np.ndarray: Processed image.
        """
        clahe_img = self._clahe_color(image, self.tile_size, self.clip_limit)
        logger.debug("Emitting processed signal")
        self.emitter.processed.emit()
        return clahe_img
    
    def _clahe_color(self, image : np.ndarray, tile_size : tuple = (8,8), clip_limit : int = 2) -> np.ndarray:
        """
        Applies contrast limited adaptive histogram equalization to the L channel of the input image in the LAB color space.

        Args:
        - image (np.ndarray): Input image to be processed.
        - tile_size (tuple): Size of the tiles for contrast limiting. Default is (8,8).
        - clip_limit (int): Threshold for contrast limiting. Default is 2.

        Returns:
        - np.ndarray: Processed image.
        """
        lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab_image)
    
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)
        clahe_l = clahe.apply(l_channel)
    
        lab_image = cv2.merge((clahe_l, a_channel, b_channel))
        return cv2.cvtColor(lab_image, cv2.COLOR_LAB2BGR)