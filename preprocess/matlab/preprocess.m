function [ panoImg_rot, panoEdge_rot, panoOmap_rot] = preprocess( inputFile, outputPath)

add_path;

%%
panoImg = imread(inputFile);
panoImg = imresize(panoImg, [1024, 2048]);
panoImg = im2double(panoImg);
%figure; imshow(panoImg)

%%
panoSep = getPanoSeperate(panoImg, 320);

%%
[ olines, vp, views, edges, panoEdge, score, angle] = getPanoEdges(panoImg, panoSep, 0.7);
%figure; imshow(panoEdge);

%%
se = strel('diamond',8);
panoEdge_dilate = imdilate(panoEdge,se);
%figure; imshow(panoEdge_dilate);
panoEdge_blur = imgaussfilt(panoEdge_dilate, [10,10]);
%figure; imshow(uint8(panoEdge_blur));

%%
[ ~, panoOmap ] = getPanoOmap( views, edges, vp );
%figure; imshow(panoOmap);

%%
vp = vp(3:-1:1,:);
[ panoImg_rot, R ] = rotatePanorama( panoImg, vp);
%figure; imshow(panoImg_rot);
panoEdge_rot = rotatePanorama(panoEdge, [], R);
%figure; imshow(panoEdge_rot);
panoOmap_rot = rotatePanorama(panoOmap, [], R);
%figure; imshow(panoOmap_rot);

%%
if ~exist(outputPath,'dir') 
    mkdir(outputPath);
end

imwrite(panoImg_rot,[outputPath 'color.png']);
imwrite(panoEdge_rot,[outputPath 'lines.png']);
imwrite(panoOmap_rot,[outputPath 'omap.png']);

end

