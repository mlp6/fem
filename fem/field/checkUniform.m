function [isUniform] = checkUniform(measurementPoints)
% function [isUniform] = checkUniform(measurementPoints)
%
% check to see if mesh is linear or nonlinear. if mesh is nonlinear, this means
% that force scaling needs to be done
%
x = unique(measurementPoints(:, 1));
y = unique(measurementPoints(:, 2));
z = unique(measurementPoints(:, 3));
isUniform = all(abs(diff(x)/(x(2)-x(1))-1 < 10^-9)) &&...
            all(abs(diff(y)/(y(2)-y(1))-1 < 10^-9)) &&...
            all(abs(diff(z)/(z(2)-z(1))-1 < 10^-9));
