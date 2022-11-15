import torch
from PIL import Image
import io

def get_yolov5():
    # local best.pt
    model = torch.hub.load('ultralytics/yolov5', 'custom', './model/best.pt', 'local')  # local repo
    model.conf = 0.5
    return model