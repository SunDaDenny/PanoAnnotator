import numpy as np
import tensorflow as tf

from ..models import *
import data_loader
import utils
import configs
params = configs.get_param()


def show_test_gt(sess, data_test_iterator, num):
	
	next_element = data_test_iterator.get_next()
	sess.run(data_test_iterator.initializer)        
	
	for i in range(0, num):
		batch = sess.run(next_element)
		utils.show_rgb(batch[0], True, "test/gt_rgb_{0}_".format(i))
		utils.show_depth(batch[1], True, "test/gt_{0}_".format(i))


def show_test_pred(sess, net, input_node, data_test_iterator, epoch, num):

	next_element = data_test_iterator.get_next()
	sess.run(data_test_iterator.initializer)
	
	for i in range(0, num):
		batch = sess.run(next_element)
		pred = sess.run(net.get_output(), feed_dict={input_node: batch[0]})
		
		utils.show_depth(pred, True, "test/epoh{0}_{1}_".format(epoch, i))
