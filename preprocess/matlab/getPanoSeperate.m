function [sepScene] = getPanoSeperate( panoImg, cutSize )

    fov = pi/3;
    xh = -pi:(pi/6):(5/6*pi);
    yh = zeros(1, length(xh));
    xp = [-3/3 -2/3 -1/3 +0/3 +1/3 +2/3 -3/3 -2/3 -1/3 +0/3 +1/3 +2/3] * pi;
    yp = [ 1/4  1/4  1/4  1/4  1/4  1/4 -1/4 -1/4 -1/4 -1/4 -1/4 -1/4] * pi;
    x = [xh xp 0     0];
    y = [yh yp +pi/2 -pi/2];

    [sepScene] = separatePano( panoImg, fov, x, y, cutSize);

end

