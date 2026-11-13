cmake_minimum_required(VERSION 3.15.3)

get_filename_component(PROJECT_NAME ${CMAKE_CURRENT_SOURCE_DIR} NAME)
project(${PROJECT_NAME})

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

set(Qt5_DIR "C:/Qt/5.12.5/msvc2017_64/lib/cmake/Qt5")
find_package(Qt5 REQUIRED COMPONENTS Core Gui Widgets)

set(ENV{DEVKIT_LOCATION} "C:/Program Files/Autodesk/devkit 2020.1")
include($ENV{DEVKIT_LOCATION}/cmake/pluginEntry.cmake)

file(GLOB_RECURSE SOURCE_FILES LIST_DIRECTORIES false
	src/*.h
	src/*.cpp
	src/*.ui
	src/*.qrc
)
include_directories(src)

set(LIBRARIES
	OpenMaya OpenMayaAnim OpenMayaFX OpenMayaRender OpenMayaUI Foundation clew Qt5Core Qt5Gui Qt5Widgets
)

build_plugin()
install(TARGETS ${PROJECT_NAME} DESTINATION "${CMAKE_CURRENT_SOURCE_DIR}/bin")