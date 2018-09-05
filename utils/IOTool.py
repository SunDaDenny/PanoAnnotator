import json
import io
import utils

try:
    to_unicode = unicode
except NameError:
    to_unicode = str


def saveSceneAsMaps(path, scene):

    edgeMap = scene.label.genLayoutEdgeMap()
    #utils.showImage(edgeMap)
    utils.saveImage(edgeMap, path + 'label_edge.png')
    
    oMap = scene.label.genLayoutOMap()
    #utils.showImage(oMap)
    #utils.saveImage(oMap, path + 'omap.png')

    normalMap = scene.label.genLayoutNormalMap()
    #utils.showImage(normalMap)
    utils.saveImage(normalMap, path + 'label_normal.png')


def saveSceneAsJson(path, scene):

    points =  scene.label.getLayoutPoints()
    pointsList = []
    for i, point in enumerate(points):
        pointDict = {
            'coords':point.coords,
            'depth':float(point.depth),
            'xyz':list(point.xyz),
            'id':point.id
        }
        pointsList.append(pointDict)
    pointsDict = {'num':len(points),
                  'points':pointsList}

    walls = scene.label.getLayoutWalls()
    wallsList = []
    for i, wall in enumerate(walls):
        wallDict = {
            'pointsIdx':[points.index(wall.gPoints[0]),
                      points.index(wall.gPoints[1])],
            'normal':list(wall.normal),
            'planeEquation':list(wall.planeEquation),
            'width': wall.width,
            'id' : wall.id
        }
        wallsList.append(wallDict)
    wallsDict = {'num':len(walls),
                 'walls':wallsList}

    data = {'name': scene.getPanoColorPath(),
            'layoutHeight': scene.label.getLayoutHeight(),
            'cameraHeight': scene.label.getCameraHeight(),
            'cameraCeilingHeight': scene.label.getCam2CeilHeight(),
            'layoutPoints':pointsDict,
            'layoutWalls':wallsDict}

    with io.open(path, 'w', encoding='utf8') as outfile:
        str_ = json.dumps(data,
                        indent=4, sort_keys=True,
                         ensure_ascii=False)
        outfile.write(to_unicode(str_))