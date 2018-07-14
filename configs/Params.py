
class Params(object):

    #MainWindows
    fileDefaultOpenPath = "D:/Dataset/"
    depthFileDefaultName = "depth_p.png"

    #Annotation
    defaultCameraHeight = 1.6
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
    pcSampleStride = 10
    meshProjSampleStep = 100