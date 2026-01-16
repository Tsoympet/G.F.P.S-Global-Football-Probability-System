cmake_minimum_required(VERSION 3.16)
project(GFPS LANGUAGES NONE)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

set(GFPS_BACKEND_DIR "${CMAKE_SOURCE_DIR}/backend")
set(GFPS_BACKEND_TEST_DIR "${GFPS_BACKEND_DIR}/tests")

add_custom_target(run_backend_tests
  COMMAND ${Python3_EXECUTABLE} -m pip install -r "${GFPS_BACKEND_DIR}/requirements.txt"
  COMMAND ${Python3_EXECUTABLE} -m pip install --upgrade pytest
  COMMAND ${Python3_EXECUTABLE} -m pytest "${GFPS_BACKEND_TEST_DIR}"
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
  COMMENT "Install backend dependencies and run pytest"
)

enable_testing()
add_test(
  NAME backend_pytest
  COMMAND ${CMAKE_COMMAND} --build "${CMAKE_BINARY_DIR}" --target run_backend_tests
)
