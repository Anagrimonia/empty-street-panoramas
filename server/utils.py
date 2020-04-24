from models.deeplab import DeepLab
from models.pix2pix import Pix2Pix

import tensorflow as tf

from skimage import color, morphology
from matplotlib import pyplot as plt
from six.moves import urllib
from skimage import measure
from pathlib import Path
from PIL import Image
import numpy as np
import tempfile
import os
import sys


CKPT_DIR = 'models/weights/'
CKPT_FILE = 'ckpt-1'

MODEL_NAME = 'mobilenetv2_coco_cityscapes_trainfine'
DOWNLOAD_URL_PREFIX = 'http://download.tensorflow.org/models/'
MODEL_URLS = 'deeplabv3_mnv2_cityscapes_train_2018_02_05.tar.gz'
TARBALL_NAME = 'deeplab_model.tar.gz'


DILATION_PATTERN = np.array([[0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
							 [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
							 [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
							 [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
							 [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
							 [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
							 [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
							 [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
							 [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
							 [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
							 [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
							 [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
							 [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
							 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
							 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
							 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
							 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])



def init_pix2pix():
	"""Creates Pix2Pix model """
	p2p = Pix2Pix(mode='test', ckpt_dir=CKPT_DIR, ckpt_name=CKPT_FILE, train_log_dir=CKPT_DIR)
	return p2p

def init_deeplab():
	"""Creates Deeplab model """
	model_dir = tempfile.mkdtemp()
	tf.io.gfile.makedirs(model_dir)

	download_path = os.path.join(model_dir, TARBALL_NAME)
	print('Downloading model...')

	urllib.request.urlretrieve(DOWNLOAD_URL_PREFIX + MODEL_URLS, download_path)
	print('Loading DeepLab model...')

	deeplab = DeepLab(download_path)
	print('Done')

	return deeplab

def compress_image(image, x):
	w, h = image.size;
	return image.resize((w // x , h // x), Image.ANTIALIAS)


# -----======= Pix2Pix tools ======-----


def normalize(real_image):
	""" Image normalization """
	real_image = (real_image / 127.5) - 1
	return real_image

def generate_fake(img, model, HEIGHT=256, WIDTH=256):
	""" Generates fake image """
	fake = tf.expand_dims(img, 0)
	return model.generator(fake)[0]

def create_new_image(pix2pix, ground, img_real, rois):
	""" Creates enhanced image """
	img_fake = img_real

	blocks = []
	bboxes = []
	coords = []

	for i in range(len(rois)):
		im_cut, bbox1, bbox2, x1y1, x2y2 = get_tile(img_real, rois[i])
		fake_block = generate_fake(im_cut, pix2pix)
		blocks.append(fake_block)
		bboxes.append((bbox1, bbox2))
		coords.append((x1y1, x2y2))

	new = insert_blocks(ground, blocks, bboxes, coords)
	return new

def insert_into_image(img_real, img_fake, bbox1, bbox2, x1y1, x2y2, HEIGHT=256, WIDTH=256):
	""" Inserts fake tile into real image """
	box_width = bbox2[0] - bbox1[0]
	box_height = bbox2[1] - bbox1[1]

	obj_width = x2y2[0] - x1y1[0]
	obj_height = x2y2[1] - x1y1[1]

	img_fake_resized = tf.image.resize(img_fake, [box_height, box_width], method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)
	img_fake_resized = img_fake_resized[obj_width:-obj_width, obj_height:-obj_height, :]
	img_real[x1y1[0]:x2y2[0], x1y1[1]:x2y2[1], :] = img_fake_resized[:]

	return img_real


def insert_blocks(img_real, blocks, bboxes, coords):
	""" Inserts fake tiles  """
	img_numpy = img_real
	for block, bbox, coord in zip(blocks, bboxes, coords):
		
		bbox1 = bbox[0]
		bbox2 = bbox[1]
		x1y1 = coord[0]
		x2y2 = coord[1]

		img_numpy = insert_into_image(img_numpy, block, bbox1, bbox2, x1y1, x2y2)

	return img_numpy

def get_tile(img, box, expand=False, HEIGHT=256, WIDTH=256):
	""" Gets a tile from image that need to be enhanced """
	wh = np.flip(img.shape[0:2])

	x1y1 = tuple((np.array(box[0:2])).astype(np.int32))
	x2y2 = tuple((np.array(box[2:4])).astype(np.int32))
	
	box_width = x2y2[0] - x1y1[0]
	box_height = x2y2[1] - x1y1[1]

	bbox1 = (x1y1[1] - box_height, x1y1[0] - box_width)
	bbox2 = (x2y2[1] + box_height, x2y2[0] + box_width)

	im_cut = img.numpy().take(range(bbox1[1], bbox2[1]), mode='wrap', axis=0).take(
							  range(bbox1[0], bbox2[0]), mode='wrap', axis=1)
	
	im_cut = tf.image.resize(im_cut, [HEIGHT, WIDTH], method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)

	return im_cut, bbox1, bbox2, x1y1, x2y2

def remove_objects(pix2pix, ground, image, bboxes):
	""" Prepares data for enhancing """
	image = tf.convert_to_tensor(image, np.float32)
	image = normalize(image)
	ground= normalize(ground)
	rois = np.array(bboxes)
	final_image = create_new_image(pix2pix, ground, image, rois)
	return final_image


# -----======= Deeplab tools ======-----


def segmentate_objects(deeplab, original_im):
	""" Segmentates image objects """
	seg_map = deeplab.run(original_im)
	image = np.array(original_im)
	image = image[...,:3]

	color = (0.0, 1.0, 0.0)
	bboxes = []

	#plt.imsave('images/seg.jpg', seg_map)

	seg_map = np.where(seg_map >= 11,-1,0)
	seg_map = morphology.dilation(seg_map, selem=morphology.disk(2))

	map_labeled = measure.label(seg_map, connectivity=1)	
	for region in measure.regionprops(map_labeled):
		if region.area > 50:
			box = region.bbox
			seg_map[box[0]:box[2], box[1]:box[3]] = np.where(seg_map[box[0]:box[2], box[1]:box[3]] == -1,1,0)
			
	seg_map = morphology.dilation(seg_map, selem=DILATION_PATTERN)

	map_labeled = measure.label(seg_map, connectivity=1)	
	for region in measure.regionprops(map_labeled):
		if region.area > 50:
			box = region.bbox
			bboxes.append(list(box))
			seg_map[box[0]:box[2], box[1]:box[3]] = np.where(seg_map[box[0]:box[2], box[1]:box[3]] == 1,-1,0)

	for c in range(3):
	  image[:, :, c] = np.where(seg_map == -1,
								color[c] * 255,
								image[:, :, c])

	return image, bboxes