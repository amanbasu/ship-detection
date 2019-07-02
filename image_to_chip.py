'''
Copyright (C) 2019 Aman Agarwal

This script is used for converting a large image tile into smaller chips.
The images have to be labeled through the LabelMe annotation tool and the 
label should be in the .json format.

Note: this file is configured for objects of only one category,
i.e., json file should contain only one category of label.

Arguments
-s: the size of the image chip (default 512x512).
-id: folder containing the labeled images.
-sd: folder to save the chips.

Ex: python image_to_chip.py -s 448
''' 

import os
import json
import glob
import argparse
import numpy as np
from PIL import Image
from scipy.misc import imsave
from sklearn.cluster import DBSCAN

def check_num(xc, yc, w, h):
    '''
    to adjust or drop the labels out of the image scope
    '''
    if xc<0:
        w = w + xc
        xc = 0.0
    elif xc>1:
        w = w - xc + 1
        xc = 1.0
    if w<0.01:
        return None

    if yc<0:
        h = h + yc
        yc = 0.0
    elif yc>1:
        h = h - yc + 1
        yc = 1.0
    if h<0.01:
        return None

    return xc, yc, w, h

def save_files(image, label, info):
    '''
    function for saving the chips of size
    IM_SIZE x IM_SIZE in the YOLO format
    '''
    
    s = IM_SIZE//2
    b = IM_SIZE

    # creates the output directory if not already exists
    if not os.path.exists(OUT_DIR):
        os.mkdir(OUT_DIR)

    for k in info.keys():
        x, y = info[k]['center'][0], info[k]['center'][1]

        # saving image chip
        iname = OUT_DIR + '/{}_{}.png'.format(label['imagePath'][:-4], k)
        # discard images smaller than IM_SIZExIM_SIZE
        try:
            imsave(iname, image[y-s:y+s, x-s:x+s, :3])
        except:
            continue

        # saving label
        file = open(iname.replace('.png', '.txt'), 'a')
        for point in info[k]['bbox']:
            [[x_bot, y_bot], [x_top, y_top]] = point
            xc = ((x_bot+x_top)//2 - x + s) / b
            yc = ((y_bot+y_top)//2 - y + s) / b
            w = abs(x_bot-x_top) / b
            h = abs(y_bot-y_top) / b

            # checks the validity of coordinates
            res = check_num(xc, yc, w, h)
            if not res:
                continue
            
            # 0 means first object
            lab = '0 {} {} {} {}\n'.format(*res)
            file.write(lab)
        file.close()
        
def main():

    # applies chipping on every image inside the folder
    for file in glob.glob(INP_DIR+'/*.json'):
        print(file)
        
        # reading files
        with open(file, 'r') as f:
            label = json.load(f)
        image = np.array(Image.open(INP_DIR+'/'+label['imagePath']))
        
        # extracting coordinates of bounding boxes
        coords, center_list = [], []
        for p in label['shapes']:
            [[x_bot, y_bot], [x_top, y_top]] = p['points']
            coords.append(p['points'])

            # stores box's center coords for clustering
            center_list.append([(x_bot+x_top)//2, (y_bot+y_top)//2])
        coords = np.array(coords)
        
        # DB-Scan algorithm for clustering
        # eps is the clustering radius
        eps = IM_SIZE//2
        dbscan = DBSCAN(min_samples=1, eps=eps)
        x = np.array(center_list)
        # y contains the index of cluster the item belongs to
        y = dbscan.fit_predict(x)
        
        # storing centroid of clusters
        info = {}
        for i in range(y.max()+1):
            # calculates the max and min coords of all the
            # bounding boxes present in the cluster
            mi_x, mi_y = x[np.where(y==i)[0]].min(axis=0)
            ma_x, ma_y = x[np.where(y==i)[0]].max(axis=0)

            item = {}
            item['center'] = [(mi_x+ma_x)//2, (mi_y+ma_y)//2]
            item['bbox'] = coords[np.where(y==i)[0]].tolist()

            info[i] = item
            
        save_files(image, label, info)

if __name__ == '__main__':
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--im_size", required=False, default=512,\
                help="the size of the image chip (default 512x512)")
    ap.add_argument("-id", "--im_dir", required=False, default='planet_image',\
                help="folder containing the labeled images")
    ap.add_argument("-sd", "--save_dir", required=False, default='dataset',\
                help="folder to save the chips")
    args = vars(ap.parse_args())
    
    IM_SIZE = args['im_size']
    INP_DIR = args['im_dir']
    OUT_DIR = args['save_dir']

    main()