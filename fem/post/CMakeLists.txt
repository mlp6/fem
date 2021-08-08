cmake_minimum_required(VERSION 3.2)
project(fem)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}")

set(SOURCE_FILES create_disp_dat_fast.c)

FIND_PACKAGE(SWIG REQUIRED)
INCLUDE(${SWIG_USE_FILE})

FIND_PACKAGE(PythonLibs)
INCLUDE_DIRECTORIES(${PYTHON_INCLUDE_PATH})

INCLUDE_DIRECTORIES(${CMAKE_CURRENT_SOURCE_DIR})

SET(CMAKE_SWIG_FLAGS "")

SET_SOURCE_FILES_PROPERTIES(create_disp_dat_fast.i PROPERTIES SWIG_FLAGS "-includeall" SWIG_MODULE_NAME create_disp_dat_fast.so)
SWIG_ADD_LIBRARY(create_disp_dat_fast LANGUAGE python TYPE MODULE SOURCES create_disp_dat_fast.i create_disp_dat_fast.c)
SWIG_LINK_LIBRARIES(create_disp_dat_fast ${PYTHON_LIBRARIES})

add_executable(create_disp_dat_fast ${SOURCE_FILES})

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
set(SCALE_DISP_DAT_SOURCE_FILES scale_disp_dat.cpp)
add_executable(scale_disp_dat ${SCALE_DISP_DAT_SOURCE_FILES})
