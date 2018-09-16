import sys
sys.path.insert(0,"../")
import os
import argparse

import configs.Params as pm
import data
import utils

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', required=True)
    args = parser.parse_args()

    labelPath = args.i
    outputPath = os.path.dirname(args.i)

    scene = data.Scene(None)
    scene.initEmptyScene()

    utils.loadLabelByJson(labelPath, scene)
    utils.saveSceneAsMaps(outputPath, scene)
