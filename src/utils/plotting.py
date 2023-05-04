import cv2
from matplotlib import pyplot as plt

def show_image(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def scale_image(image, scale_factor=None):
    if not scale_factor:
        max_resolution = (1920, 1080)
        im_height, im_width = image.shape[:2]
        scale_factor = min(max_resolution[0] / im_width, max_resolution[1] / im_height)
    return cv2.resize(image, None, fx=scale_factor, fy=scale_factor), scale_factor

def plot_line(line, title):
    plt.plot(line)
    plt.title(title)
    plt.show()