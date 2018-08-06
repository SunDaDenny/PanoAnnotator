
class Params(object):

    #MainWindows
    fileDefaultOpenPath = "D:/Dataset/Test/all/"
    depthFileDefaultName = "pano_depth.png"
    linesFileDefaultName = "pano_edge_07.png"
    omapFileDefaultName = "pano_omap_07.png"

    #Annotation
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