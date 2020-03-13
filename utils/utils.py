import skimage.io,  skimage.transform
import numpy as np
import torch 
import cv2

try:
    from picamera import PiCamera
    def nativ_image():
        with PiCamera() as camera:
            camera.rotation = 180
            camera.resolution = (1920, 1080)
            camera.framerate = 15
            frame = np.empty((1080,1920,3), dtype=np.uint8)
            camera.capture(frame, 'rgb')
        return frame
except:
    # cam = cv2.VideoCapture(0)
    # cam.set(3, 1280)
    # cam.set(4, 720)
    def nativ_image():
        cam = cv2.VideoCapture(0)
        cam.set(3, 1280)
        cam.set(4, 720)
        ret, frame = cam.read()
        cam.release()
        return frame


def normalize(img, mean=128, std=128):
    img = (img * 256 - mean) / std
    return img

def crop_center(img, cropx, cropy):
    """Code from Loading_Pretrained_Models.ipynb - a Caffe2 tutorial"""
    y, x, c = img.shape
    startx = x // 2 - (cropx // 2)
    starty = y // 2 - (cropy // 2)
    return img[starty:starty + cropy, startx:startx + cropx]

def prepare_tensor(inputs):
    NHWC = np.array(inputs)
    NCHW = np.swapaxes(np.swapaxes(NHWC, 1, 3), 2, 3)
    tensor = torch.from_numpy(NCHW)
    tensor = tensor.float()
    return tensor

def rescale(img, input_height, input_width):
    return cv2.resize(img, (input_height, input_width), interpolation =cv2.INTER_AREA)

def load_image(image_path):
    return skimage.io.imread(image_path)

def image_to_float(img):
    img = skimage.img_as_float(img)
    if len(img.shape) == 2:
        img = np.array([img, img, img]).swapaxes(0, 2)
    return img

def prepare_input(img):
    if isinstance(img, str): # assuming url
        img = load_image(img)
    img = image_to_float(img)
    img = rescale(img, 300, 300)
    img = crop_center(img, 300, 300)
    img = normalize(img)
    return img

def get_image():
    frame = nativ_image()
    size = min(frame.shape[0], frame.shape[1])
    top =  (frame.shape[1] - size)//2
    left =  (frame.shape[0] - size)//2
    frame = frame[left: left +size, top: top + size]
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return frame, size


def get_person(image, location, size):
    x, y, w, h = list(map(lambda l: max(0, int(l*size)), location))
    window = min(w, h)
    if w > h:
        diff = (w - h)//2 
        x_start = x+diff
        im = image[y: y+h, x_start: x_start+h]
    else:
        im = image[y: y+window, x: x+window]
    return im

    