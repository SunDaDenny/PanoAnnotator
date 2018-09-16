function [ panoout ] = combineViews( Imgs, width, height )
%COMBINEVIEWS Combine multiple perspective views to panorama
%   Imgs: same format as separatePano
%   width,height: size of panorama

panoout = zeros(height, width, size(Imgs(1).img,3));
panowei = zeros(height, width, size(Imgs(1).img,3));

idxAll = [1:length(Imgs)];
idxHor = [1:12];
idxUp = [13:24];
idxDown = [25:36];
special = [1:9,13:24,25:28,31,33,37:54,60:76,81,86:98];

for i = idxAll
    
    [sphereImg validMap] = ...
        im2Sphere( Imgs(i).img, Imgs(i).fov, width, height, Imgs(i).vx, Imgs(i).vy);
    sphereImg(~validMap) = 0;

    panoout = panoout + sphereImg;
    panowei = panowei + validMap;
    
end
panoout(panowei==0) = 0;
panowei(panowei==0) = 1;
panoout = panoout./double(panowei);

end

