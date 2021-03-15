import os
import sys
import time
import json

import cv2
import numpy as np


def get_starrs(path):
    with open(path) as f:
        return json.load(f)['Starr'].keys()


def get_icon(path, resolution= 128 ** 2):
    icon = cv2.imread(path)
    h, w, c = icon.shape
    scale = (resolution / (h * w)) ** 0.5
    return cv2.resize(icon, None, fx=scale, fy=scale)


def crop(im):

    h, w, c = im.shape

    center = int(h / 2)
    mask = np.zeros(im.shape, np.uint8)
    cv2.circle(mask, (center, center), radius=center, color=(255, 255, 255), thickness=-1)

    im = im & mask

    return im


def crop_r(im):

    h, w, c = im.shape

    center = int(h / 2)
    mask = np.zeros(im.shape, np.uint8)
    cv2.circle(mask, (center, center), radius=center, color=(255, 255, 255), thickness=-1)

    mask = im | mask

    im |= mask

    im = 255 - im

    return im

def path_exists(path):
    return os.path.exists(path)

def main():
    argv = sys.argv
    episode_number = argv[1]

    concast_path = os.path.abspath('..')
    json_path = os.path.join(concast_path, f'postproduction/json/episode{episode_number}.json')
    impath = os.path.join(concast_path, f'photos/eyecatch/episode{episode_number}.jpg')

    assert path_exists(json_path), f'path not found: {json_path}'
    assert path_exists(impath), f'path not found: {impath}'

    starrs = get_starrs(json_path)

    im_starrs = []

    for starr in starrs:
        if starr == 'MainPersonality':
            starr += f'-{np.random.randint(1, 3)}'

        icon_path = os.path.join(concast_path, f'photos/starrings/{starr}.jpg')
        assert path_exists(json_path), f'path not found: {json_path}'

        icon = get_icon(icon_path)
        icon = crop(icon)
        im_starrs.append(icon)

    im = cv2.imread(impath)
    overlay = im.copy()

    x, y, w, h = cv2.selectROI(f'resize', im)

    size = min(w, h)

    alpha = 0.3

    cv2.rectangle(overlay, (x, y), (x + size, y + size), (255, 255, 255, 0.3), cv2.FILLED)

    im = cv2.addWeighted(overlay, alpha, im, 1 - alpha, 0)

    im = im[y: y + size, x: x + size]

    concast_icon_path = os.path.join(concast_path, 'concast.png')
    assert path_exists(concast_icon_path), f'path not found: {concast_icon_path}'

    concast_icon = get_icon(concast_icon_path)

    roi = im[-(20 + concast_icon.shape[0]):-20, 30: 30 + concast_icon.shape[1]]
    im[-(20 + concast_icon.shape[0]):-20, 30: 30 + concast_icon.shape[1]] = concast_icon

    i = 0
    for im_starr in im_starrs[::-1]:

        assert im_starr.shape[0]==im_starr.shape[1], f'starr icon has to be square ({im_starr.shape[0]}!={im_starr.shape[1]})'
        start_x = 40
        start_y = 20
        step = 168
        roi = im[-(start_y + im_starr.shape[0]):-(start_y), -(start_x + step * i + im_starr.shape[1]):-(start_x + step * i)]
        cropped_mask = crop_r(im_starr.copy())
        masked_roi = cv2.bitwise_and(roi, cropped_mask)
        final_roi = cv2.bitwise_or(masked_roi, im_starr)
        im[-(start_y + im_starr.shape[0]):-(start_y), -(start_x + step * i + im_starr.shape[1]):-(start_x + step * i)] = final_roi

        i += 1


    cv2.imshow('image', im)
    k = cv2.waitKey(0)

    if k == ord('q'):
        print(f'failed to save icon-{episode_number}.jpg')

    else:
        cv2.imwrite(os.path.join(concast_path, f'photos/editted-icon/icon-{episode_number}.jpg'), im)
        print(f'saved icon-{episode_number}.jpg')

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
