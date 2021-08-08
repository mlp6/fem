cmake_minimum_required(VERSION 3.2)
project(fem)
find_package(PythonExtensions REQUIRED)

add_library(_create_disp_dat MODULE fem/post/_create_disp_dat.c)
python_extension_module(_create_disp_dat)
install(TARGETS _create_disp_dat LIBRARY DESTINATION create_disp_dat)

add_subdirectory(fem)
