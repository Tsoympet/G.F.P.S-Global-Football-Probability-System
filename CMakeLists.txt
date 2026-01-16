cmake_minimum_required(VERSION 3.16)
project(GFPS LANGUAGES NONE)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

set(GFPS_BACKEND_DIR "${CMAKE_SOURCE_DIR}/backend")
set(GFPS_BACKEND_TEST_DIR "${GFPS_BACKEND_DIR}/tests")
set(GFPS_BACKEND_DEV_REQUIREMENTS "${GFPS_BACKEND_DIR}/requirements-dev.txt")
set(GFPS_SKIP_PIP_INSTALL OFF CACHE BOOL "Skip pip install when running CMake test target")

add_custom_target(install_backend_deps
  COMMAND ${Python3_EXECUTABLE} -m pip install --upgrade -r "${GFPS_BACKEND_DEV_REQUIREMENTS}"
  COMMENT "Install backend dependencies (mutates user Python environment)"
)

add_custom_target(run_backend_tests
  COMMAND ${Python3_EXECUTABLE} -m pytest "${GFPS_BACKEND_TEST_DIR}"
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
  COMMENT "Run backend pytest suite (requires deps preinstalled)"
)
if(NOT GFPS_SKIP_PIP_INSTALL)
  add_dependencies(run_backend_tests install_backend_deps)
endif()

enable_testing()
add_test(
  NAME backend_pytest
  COMMAND ${Python3_EXECUTABLE} -m pytest "${GFPS_BACKEND_TEST_DIR}"
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
)
