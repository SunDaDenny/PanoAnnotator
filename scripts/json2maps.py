import sys
sys.path.insert(0,"../")
import os

import configs.Params as pm
import data
import utils

filePath = 'D:/Dataset/Test/io/001/'
#colorPath = os.path.join(filePath, pm.colorFileDefaultName)
labelPath = os.path.join(filePath, pm.labelFileDefaultName)
outputPath = filePath


scene = data.Scene(None)
scene.initEmptyScene()


utils.loadLabelByJson(labelPath, scene)
#utils.saveSceneAsMaps(outputPath, scene)

edgeMap = utils.genLayoutEdgeMap(scene, pm.layoutMapSize)
utils.showImage(edgeMap)

oMap = utils.genLayoutOMap(scene, pm.layoutMapSize)
utils.showImage(oMap)

normalMap = utils.genLayoutNormalMap(scene, pm.layoutMapSize)
utils.showImage(normalMap)

depthMap = utils.genLayoutDepthMap(scene, pm.layoutMapSize)
utils.showImage(depthMap)

