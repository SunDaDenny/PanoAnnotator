function [ olines, vp, views, edges, panoEdge, score, angle] = getPanoEdges(img, sepScene, qError )

numScene = length(sepScene);
edge(numScene) = struct('img',[],'edgeLst',[],'vx',[],'vy',[],'fov',[]);
for i = 1:numScene
    cmdline = sprintf('-q %f ', qError);
    [ edgeMap, edgeList ] = lsdWrap( sepScene(i).img, cmdline);
%     [edgeList, edgeMap] = getLargeConnectedEdges(sepScene(i).img, thresh);
    edge(i).img = edgeMap;
    edge(i).edgeLst = edgeList;
    edge(i).fov = sepScene(i).fov;
    edge(i).vx = sepScene(i).vx;
    edge(i).vy = sepScene(i).vy;
    edge(i).panoLst = edgeFromImg2Pano( edge(i) );
end

[lines,olines] = combineEdgesN( edge);


%% compute vanishing point and refine line segments
clines = lines;
for iter = 1:3
    fprintf('*************%d-th iteration:****************\n', iter);
    [mainDirect, score, angle] = findMainDirectionEMA( clines );
    
    [ type, typeCost ] = assignVanishingType( lines, mainDirect(1:3,:), 0.1, 10 ); 
    lines1 = lines(type==1,:);
    lines2 = lines(type==2,:);
    lines3 = lines(type==3,:);

    lines1rB = refitLineSegmentB(lines1, mainDirect(1,:), 0);
    lines2rB = refitLineSegmentB(lines2, mainDirect(2,:), 0);
    lines3rB = refitLineSegmentB(lines3, mainDirect(3,:), 0);

    clines = [lines1rB;lines2rB;lines3rB];
end

%imgres = imresize(img, [512 1024]);
imgSize = size(img);
convas = zeros(imgSize);
panoEdge1r = paintParameterLine( lines1rB, imgSize(2), imgSize(1), convas);
panoEdge2r = paintParameterLine( lines2rB, imgSize(2), imgSize(1), convas);
panoEdge3r = paintParameterLine( lines3rB, imgSize(2), imgSize(1), convas);
panoEdger = cat(3, panoEdge1r, panoEdge2r, panoEdge3r);

%% output
olines = clines;
vp = mainDirect;

views = sepScene;
edges = edge;
panoEdge = panoEdger;


end

