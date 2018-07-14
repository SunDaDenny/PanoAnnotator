from matplotlib import pyplot as plt
from PIL import Image

plt.ioff()

def show_rgb(img, save, output=''):
	for i in range(0, img.shape[0]):
		fig = plt.figure()
		plt.imshow(img[i] / 255.0)
		if(save):
			plt.savefig(output + str(i) + ".png")
		else:
			plt.show()
		plt.close(fig)

def show_depth(depth, save, output=''):    
	for i in range(0, depth.shape[0]):
		fig = plt.figure()
		ii = plt.imshow(depth[i,:,:,0], interpolation='nearest',cmap='jet')
		plt.clim(0,6)
		fig.colorbar(ii)
		if(save):
			plt.savefig(output + str(i) + ".png")
		else:
			plt.show()
		plt.close(fig)

def show_list_curve(epoch_list, data_list, ylabel, save, output=''):
	
	plt.plot(epoch_list, data_list)
	plt.xlabel("Epochs")
	plt.ylabel(ylabel)
	plt.savefig(output)

	plt.close()
	