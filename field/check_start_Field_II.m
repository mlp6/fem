function check_Field_II
% function check_Field_II
% check that Field II is in the Matlab search path
test_function_name = 'field_init';
if ~exist(test_function_name),
    error('Please add Field II to your Matlab path');
else,
    disp('Starting the Field II simulation');
    field_init(-1)
end
