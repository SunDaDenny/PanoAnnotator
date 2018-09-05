
class Params(object):

    #MainWindows
    fileDefaultOpenPath = "D:/Dataset/iStaging/0001~0050"
    depthFileDefaultName = "pano_depth_none.png"
    linesFileDefaultName = "pano_edge.png"
    omapFileDefaultName = "pano_omap.png"


    #Input
    keyDict = {'none':0, 'ctrl':1, 'shift':2, 'alt':3}

    #Annotation
    layoutMapSize = [512, 1024, 3]

    defaultCameraHeight = 1.8
    defaultLayoutHeight = 3.2

    layoutHeightSampleRange = 0.3
    layoutHeightSampleStep = 0.01 

    #MonoView
    monoViewFov = (-1, 60)

    #ResultView
    resultPointColor = [(0.0, 0.5, 0.5),
                        (0.5, 0.5, 0.0),
                        (0.5, 0.0, 0.5)]

    #PanoTool
    pcSampleStride = 30
    meshProjSampleStep = 30