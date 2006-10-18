function eff = contrast_efficiency(true_les, center, diam, filename)

clf;
load(filename);
pixel = 0.2;
center_j = (center/pixel)-1;
center_i = size(matrix,1)./2.;
rad =(diam/pixel)/2.0;
sum = 0; count = 0; 
image =  matrix;
for row=1:size(matrix,1)
     for col=1:size(matrix,2)
if((row <= center_i+rad) & (row >= center_i-rad))
     if((col <= center_j+rad) & (col >=  center_j-rad))
     distance = sqrt((row-center_i)^2+(col-center_j)^2);
     if (distance <= rad)
     sum = sum + matrix(row,col);
     count = count + 1;
     image(row,col) = 0;
     end
     end
end
end
end

     imshow(image);


raw_mean = sum/count
model_con = 1 -  raw_mean;
true_bckd = 4.0;
true_con = 1-(true_bckd/true_les)
eff = model_con/true_con
