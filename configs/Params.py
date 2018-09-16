
class Params(object):

    #MainWindows
    fileDefaultOpenPath = "D:"

    labelFileDefaultName = "label.json"

    colorFileDefaultName = "color.png"#"pano_color.png"
    depthFileDefaultName = "depth_gt.png"#"pano_depth_none.png"
    linesFileDefaultName = "lines.png"#"pano_edge.png"
    omapFileDefaultName = "omap.png"#pano_omap.png"

    #Input
    keyDict = {'none':0, 'ctrl':1, 'shift':2, 'alt':3, 'object':4}

    #Annotation
    layoutMapSize = [512, 1024, 3]

    defaultCameraHeight = 1.8
    defaultLayoutHeight = 3.2

    layoutHeightSampleRange = 0.3
    layoutHeightSampleStep = 0.01 

    #MonoView
    monoViewFov = (-1, 90)

    #PanoTool
    pcSampleStride = 30
    meshProjSampleStep = 30