# Migration Notes

- New C++20 backend scaffold added under `backend_cpp` using Drogon, nlohmann/json, OpenSSL, SQLite3, and Catch2.
- Routes mirror existing FastAPI endpoints: `/health`, `/auth/login`, `/fixtures`, `/predict`, `/value`.
- JWT-based auth uses HS256 with configurable secret and expiry in `config/config.json`.
- SQLite schema bootstrapped via `storage/Schema.sql` and initialized on startup.
- Probability and EV engines implemented for parity with Python service (Poisson 1X2, EV = p*odds - 1).
