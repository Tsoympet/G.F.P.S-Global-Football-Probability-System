cmake_minimum_required(VERSION 3.20)
project(gfps_cpp_backend LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

include(FetchContent)

set(DEFAULT_BUILD_TYPE "Release")
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE ${DEFAULT_BUILD_TYPE} CACHE STRING "Build type" FORCE)
endif()

# Dependencies
FetchContent_Declare(
    drogon
    GIT_REPOSITORY https://github.com/drogonframework/drogon.git
    GIT_TAG v1.9.6
)
FetchContent_Declare(
    json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG v3.11.3
)
FetchContent_Declare(
    sqlite_modern_cpp
    GIT_REPOSITORY https://github.com/SqliteModernCpp/sqlite_modern_cpp.git
    GIT_TAG v3.2
)
FetchContent_Declare(
    catch2
    GIT_REPOSITORY https://github.com/catchorg/Catch2.git
    GIT_TAG v3.5.3
)

set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
set(DROGON_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(DROGON_BUILD_TESTS OFF CACHE BOOL "" FORCE)

FetchContent_MakeAvailable(drogon json sqlite_modern_cpp catch2)

find_package(OpenSSL REQUIRED)
find_package(SQLite3 REQUIRED)

# Core library
add_library(gfps_backend_core
    src/App.cpp
    src/controllers/HealthController.cpp
    src/controllers/AuthController.cpp
    src/controllers/FixturesController.cpp
    src/controllers/PredictionsController.cpp
    src/controllers/ValueController.cpp
    src/services/ProbabilityEngine.cpp
    src/services/EVEngine.cpp
    src/services/ConfidenceEngine.cpp
    src/models/Match.cpp
    src/models/Team.cpp
    src/models/League.cpp
    src/storage/Database.cpp
    src/auth/JwtMiddleware.cpp
    src/utils/JsonUtils.cpp
    src/utils/TimeUtils.cpp
)

target_include_directories(gfps_backend_core
    PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_link_libraries(gfps_backend_core
    PUBLIC drogon json::json sqlite_modern_cpp OpenSSL::SSL OpenSSL::Crypto SQLite::SQLite3
)

target_compile_options(gfps_backend_core PRIVATE -Wall -Wextra -Werror -Wpedantic)

# Application executable
add_executable(gfps_backend src/main.cpp)
target_link_libraries(gfps_backend PRIVATE gfps_backend_core)

# Tests
enable_testing()
add_executable(gfps_backend_tests
    tests/test_probability.cpp
    tests/test_ev.cpp
    tests/test_api.cpp
)

target_include_directories(gfps_backend_tests PRIVATE src)

target_link_libraries(gfps_backend_tests PRIVATE gfps_backend_core Catch2::Catch2WithMain)

include(CTest)
include(Catch)
catch_discover_tests(gfps_backend_tests)

install(TARGETS gfps_backend RUNTIME DESTINATION bin)
