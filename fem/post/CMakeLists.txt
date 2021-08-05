cmake_minimum_required(VERSION 3.2)
project(fem)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

set(SOURCE_FILES
    scale_disp_dat.cpp)

add_executable(scale_disp_dat ${SOURCE_FILES})
