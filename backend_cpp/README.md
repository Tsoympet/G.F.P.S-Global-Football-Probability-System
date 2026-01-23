# GFPS C++ Backend

A lightweight Drogon-based C++20 backend for the Global Football Probability System. Provides health, authentication, fixtures, probability, and value endpoints, mirroring the FastAPI contract where possible.

## Prerequisites
- CMake >= 3.20
- A C++20 compiler
- OpenSSL, SQLite3 development headers (for linking)

## Build
```bash
cd backend_cpp
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

## Run
```bash
cd backend_cpp/build
./gfps_backend
```
The server listens on `127.0.0.1:8000` by default, configured via `config/config.json`.

## Tests
```bash
cd backend_cpp
cmake --build build --target gfps_backend_tests
ctest --test-dir build
```

## Authentication
`POST /auth/login` returns an HS256 JWT. Include it as `Authorization: Bearer <token>` for protected routes.

## Desktop Integration
Desktop clients can call the same HTTP endpoints exposed by the FastAPI backend; this server mirrors those paths and payloads for local or production swap.
