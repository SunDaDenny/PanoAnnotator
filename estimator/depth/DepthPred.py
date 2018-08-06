import numpy as np
import tensorflow as tf
from PIL import Image

from .models import *

MODEL_FILE = 'estimator/depth/models/trained/NYU_ResNet-UpProj_pano_512_20_epoch.ckpt'

IMAGE_SIZE = [512, 1024]
DEPTH_SIZE = [256, 512]

INPUT_SHAPE = [None, IMAGE_SIZE[0], IMAGE_SIZE[1], 3]
OUTPUT_SHAPE = [None, DEPTH_SIZE[0], DEPTH_SIZE[1], 1]

BATCH_SIZE = 4

DEPTH_RANGE = [0, 10]

class DepthPred(object):

    def __init__(self, parent=None):

        self.__isAvailable = False

        self.input_node = tf.placeholder(tf.float32, shape = INPUT_SHAPE)
        self.net = ResNet50UpProj({'data':self.input_node}, BATCH_SIZE, 1, False)

        self.y_predict = self.net.get_output()
        self.y_label = tf.placeholder(tf.float32, shape = OUTPUT_SHAPE, name = "y_label")

        self.sess = tf.Session()
        self.saver = tf.train.Saver()
        
        self.initEstimator()
        

    def initEstimator(self):

        init_op = tf.variables_initializer(tf.global_variables())
        print("sess init")
        self.sess.run(init_op)
        print("model loading")
        self.saver.restore(self.sess, MODEL_FILE)
        print("done")
        self.__isAvailable = True

    def predict(self, image):
        #image : PIL.Image

        image = image.resize((IMAGE_SIZE[1], IMAGE_SIZE[0]), Image.ANTIALIAS)
        image_data = np.asarray(image, dtype="float32" )
        image_data = image_data[:,:,0:3]
        image_data = np.expand_dims(image_data, axis = 0)

        input_data = np.zeros((BATCH_SIZE,INPUT_SHAPE[1],INPUT_SHAPE[2],INPUT_SHAPE[3]))
        input_data[0] = image_data
        #print(input_data.shape)

        pred = self.sess.run(self.net.get_output(), feed_dict={self.input_node: input_data})
        #print(pred.shape)        

        return np.squeeze(pred[0])