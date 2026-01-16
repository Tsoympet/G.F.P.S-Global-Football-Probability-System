cmake_minimum_required(VERSION 3.16)
project(GFPS LANGUAGES NONE)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

set(GFPS_BACKEND_DIR "${CMAKE_SOURCE_DIR}/backend")
set(GFPS_BACKEND_TEST_DIR "${GFPS_BACKEND_DIR}/tests")

add_custom_target(install_backend_deps
  COMMAND ${Python3_EXECUTABLE} -m pip install --upgrade -r "${GFPS_BACKEND_DIR}/requirements.txt"
  COMMAND ${Python3_EXECUTABLE} -m pip install --upgrade pytest
  COMMENT "Install backend dependencies (mutates user Python environment)"
)

add_custom_target(run_backend_tests
  COMMAND ${Python3_EXECUTABLE} -m pytest "${GFPS_BACKEND_TEST_DIR}"
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
  COMMENT "Run backend pytest suite (requires deps preinstalled)"
)
add_dependencies(run_backend_tests install_backend_deps)

enable_testing()
add_test(
  NAME backend_pytest
  COMMAND ${Python3_EXECUTABLE} -m pytest "${GFPS_BACKEND_TEST_DIR}"
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
)
