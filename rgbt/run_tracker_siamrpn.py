from __future__ import absolute_import, division, print_function, unicode_literals

import os
import cv2
import torch
import numpy as np
from PIL import Image
import imageio
from siamrpn_pp.models.model_builder import ModelBuilder
from siamrpn_pp.tracker.tracker_builder import build_tracker
from dataset.votRGBTdatabase import VOTRGBTDataset
from tools.args_temp import args
from torch.autograd import Variable
from torchvision import datasets, transforms
from siamrpn_model.siamrpn_r50 import config as cfg
import os




def imread(path):
    return imageio.imread(path)

def imsave(path, arr):
    imageio.imwrite(path, arr)

def imresize(image, size, interp='nearest'):
    pil_image = Image.fromarray(image)
    resized_image = pil_image.resize(size, Image.NEAREST if interp == 'nearest' else Image.BILINEAR)
    return np.array(resized_image)

def get_image(path, height=256, width=256, mode='RGB'):
    image = Image.open(path).convert(mode)
    if height is not None and width is not None:
        image = imresize(np.array(image), [height, width], interp='nearest')
    return image

def get_test_images(paths, height=None, width=None, mode='RGB'):
    if isinstance(paths, str):
        paths = [paths]
    images = []
    for path in paths:
        image = get_image(path, height, width, mode=mode)
        images.append(image)
    images = np.stack(images, axis=0)
    return images

def _get_image(image_file: str, mode: str): 
    image = get_test_images(image_file, mode=mode)
    return image

def vis(idx, img, img_ir, gt_bbox, gt_bbox_rgb, pred_bbox, lost_number):
    img = cv2.rectangle(img, (gt_bbox[0], gt_bbox[1]),
                         (gt_bbox[0] + gt_bbox[2], gt_bbox[1] + gt_bbox[3]), (255, 0, 0), 3)
    img = cv2.rectangle(img, (gt_bbox_rgb[0], gt_bbox_rgb[1]),
                        (gt_bbox_rgb[0] + gt_bbox_rgb[2], gt_bbox_rgb[1] + gt_bbox[3]), (0, 255, 0), 3)

    bbox = list(map(int, pred_bbox))
    img = cv2.rectangle(img, (bbox[0], bbox[1]),
                  (bbox[0] + bbox[2], bbox[1] + bbox[3]), (0, 255, 255), 3)

    cv2.putText(img, str(idx), (40, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.putText(img, lost_number, (40, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    img_ir = cv2.rectangle(img_ir, (gt_bbox[0], gt_bbox[1]),
                        (gt_bbox[0] + gt_bbox[2], gt_bbox[1] + gt_bbox[3]), (255, 0, 0), 3)
    img_ir = cv2.rectangle(img_ir, (gt_bbox_rgb[0], gt_bbox_rgb[1]),
                           (gt_bbox_rgb[0] + gt_bbox_rgb[2], gt_bbox_rgb[1] + gt_bbox[3]), (0, 255, 0), 3)

    img_ir = cv2.rectangle(img_ir, (bbox[0], bbox[1]),
                        (bbox[0] + bbox[2], bbox[1] + bbox[3]), (0, 255, 255), 3)

    img_ = np.concatenate((img, img_ir), axis=1)
    cv2.imshow('Test', img_)
    cv2.waitKey(1)

with torch.no_grad():
    root_path = os.path.dirname(__file__)

    cfg.CUDA = torch.cuda.is_available()
    device = torch.device('cuda' if cfg.CUDA else 'cpu')
    model = ModelBuilder()
    model.load_state_dict(torch.load(root_path + args.snapshot, map_location=lambda storage, loc: storage.cpu()))
    model.eval().to(device)

    tracker = build_tracker(model)

    dataset = VOTRGBTDataset()
    visualization = True
    mode = 'RGB'

    for sequence in dataset:
        print('Tracker: {},  Sequence: {}'.format('PYSOT', sequence.name))
        colorimage = _get_image(sequence.frames_color[0], mode)
        infraredimage = _get_image(sequence.frames_infrared[0], mode)
        colorimage_np = colorimage.squeeze()
        infraredimage_np = infraredimage.squeeze()
        tracker.init(colorimage_np, infraredimage_np, sequence.init_state)

        tracked_bb = [sequence.init_state]
        count = 0
        for frame_color, frame_infrared, gt in zip(sequence.frames_color[1:], sequence.frames_infrared[1:], sequence.ground_truth_rect[1:]):
            count += 1
            colorimage = _get_image(frame_color, mode)
            infraredimage = _get_image(frame_infrared, mode)
            colorimage_np = colorimage.squeeze()
            infraredimage_np = infraredimage.squeeze()

            outputs = tracker.track(colorimage_np, infraredimage_np)
            state = list(map(int, outputs['bbox']))

            gbbox = gt.tolist()
            gt_bbox = list(map(int, gbbox))

            gt_bbox_rgb = gt_bbox
            if visualization:
                seq_name = sequence.name + ' :' + str(count)
                vis(count, colorimage_np, infraredimage_np, gt_bbox, gt_bbox_rgb, state, seq_name)

            tracked_bb.append(state)
