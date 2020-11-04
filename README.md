# Building a complete Ship detection algorithm using YOLOv3 and Planet satellite images from scratch

The repository contains the code for [this](https://medium.com/intel-software-innovators/ship-detection-in-satellite-images-from-scratch-849ccfcc3072) article, and is about building a custom object detection algorithm from scratch for satellite imagery.

Information about the files and folders
- [download_planet_image.py](https://github.com/amanbasu/ship-detection/blob/master/download_planet_image.py): for downloading the Planet image tiles. Requires the planet api-key and AOI geometry (in geojson).
- [image_to_chip.py](https://github.com/amanbasu/ship-detection/blob/master/image_to_chip.py): converts the labeled satellite tiles into chips of smaller size.
- [train.txt](https://github.com/amanbasu/ship-detection/blob/master/train.txt) and [test.txt](https://github.com/amanbasu/ship-detection/blob/master/test.txt): contains the training and test image paths
- [dataset](https://github.com/amanbasu/ship-detection/tree/master/dataset): holds the full labeled dataset for training the model.
- [ground_truth](https://github.com/amanbasu/ship-detection/tree/master/ground_truth): contains the images with their ground truth bounding boxes.

The dataset was trained on the YOLOv3 model and darknet framework. 

### Getting darknet
Follow these commands for setting up the darknet framework

```bash
git clone https://github.com/pjreddie/darknet
cd darknet
make
```

Get the pre-trained weights from here.

```bash
wget https://pjreddie.com/media/files/darknet53.conv.74
```

Try running the detector to confirm the installation.

```bash
./darknet detect cfg/yolov3.cfg yolov3.weights data/dog.jpg
```

### Preparing the Config files
Darknet requires certain files to know how and what to train.

- data/ship.names
- cfg/ship.data
- cfg/yolov3-ship.cfg

`.names` file contains the name of the object categories you want to detect. Now, since we have got only one object category (ship), the file will be like [this](https://github.com/amanbasu/ship-detection/blob/master/darknet_files/ship.names). This name is shown over the bounding box in the output. For more than one object, every name has to be written in a separate line.

`.data` file contains information about the training data. The details in [this](https://github.com/amanbasu/ship-detection/blob/master/darknet_files/ship.data) file are pretty much self-explanatory. `names` variable will contain the path to the object names file you just defined. `backup` stores the checkpoint of the model during training. The `train.txt` and `test.txt` files will contain the path to the training and testing images.

The final step is to set up the `.cfg` [file](https://github.com/amanbasu/ship-detection/blob/master/darknet_files/yolov3-ship.cfg) which contains the information about the YOLO network architecture. For that, just copy the `cfg/yolov3.cfg` file in the darknet folder, paste it as `cfg/yolov3-ship.cfg`, and make the following changes:

1. The variable `batch` defines the number of images used for one training step, while `subdivision` is the number of mini-batches. For example, with `batch=64` and `subdivision=4`, one training step will require four mini-batches with `64/4=16` images each before updating the parameters. These variables can be set according to your CPU/GPU memory size.

2. `width` and `height` represent the size of the input image, in our case, it's 512.

3. YOLOv3 outputs the boxes in 3 different resolutions, with each label represented by five numbers (i.e., probability/class confidence, x, y, width, and height). Therefore, the number of filters in the last layer is calculated by the formula 

   `filters = (classes + 5) * 3`

   Since we have got only 1 class, the number of filters become 18. Now replace each occurrence of `classes=80` by `classes=1` in the file (at line 610, 696, and 783).

4. Also, replace the `filters=255` line by `filters=18` each time the `classes` variable occurs (at line 603, 689, and 776).

### Training

```bash
./darknet detector train cfg/ship.data cfg/yolov3-ship.cfg darknet19_448.conv.23
```

### Testing

```bash
./darknet detector test cfg/ship.data cfg/yolov3.cfg backup/backup_file.weights test_file.jpg
```
