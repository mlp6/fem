[SortedNodeIDs,x,y,z]=SortNodeIDs('/nefs/mlp6/nonlinear/gfp/nodes.asc');
load nodeID_count

fid = fopen('node_data.bin','rb')
slicey = zeros(size(SortedNodeIDs,1),size(SortedNodeIDs,3),2e3);
for i=1:size(SortedNodeIDs,1)
  i
  for k=1:size(SortedNodeIDs,3)
    sk = nodeID_count(SortedNodeIDs(i,1,k),2)+3;
    fseek(fid,sk*4,'bof');
    siz = nodeID_count(SortedNodeIDs(i,1,k)+1,2)-sk;
    tmp = fread(fid,siz,'real*4');
    slicey(i,k,1:length(tmp)) = tmp;
  end
end
fclose(fid);

figure(1)
imagesc(sum(slicey.^2,3))
colorbar
figure(2),plot(squeeze(sum(slicey(1,:,:).^2,3)))

fid = fopen('node_data.bin','rb')
slicex = zeros(size(SortedNodeIDs,2),size(SortedNodeIDs,3),2e3);
for j=1:size(SortedNodeIDs,2)
  j
  for k=1:size(SortedNodeIDs,3)
    sk = nodeID_count(SortedNodeIDs(1,j,k),2)+3;
    fseek(fid,sk*4,'bof');
    siz = nodeID_count(SortedNodeIDs(1,j,k)+1,2)-sk;
    tmp = fread(fid,siz,'real*4');
    slicex(j,k,1:length(tmp)) = tmp;
  end
end
fclose(fid);

figure(3)
imagesc(sum(slicex.^2,3))
colorbar
figure(4),plot(squeeze(sum(slicex(1,:,:).^2,3)))
