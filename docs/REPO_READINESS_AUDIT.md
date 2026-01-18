# Repository Readiness Audit (2026-01-17)

This audit focuses on **developer install/run readiness** for Windows, macOS, and Linux.
It complements the broader security/architecture audit already documented in `docs/AUDIT_REPORT.md`.

---

## ✅ What is already in place

- **Clear entry points** for backend (`backend.main:app`) and desktop UI (`GFPS/desktop`).
- **Environment template** (`.env.example`) with required/optional variables.
- **Docker tooling** via `Dockerfile` and `infrastructure/docker-compose.yml`.
- **Existing setup guidance** in `README.md` and `docs/LOCAL_SETUP.md`.

---

## 🧭 Readiness findings

### 1) Environment defaults could break local flows

- `.env.example` defaults `FRONTEND_BASE_URL` to `https://example.com`.
- This causes local password reset URLs to point at a non-local domain.

**Fix applied:**
- Local setup now explicitly sets `FRONTEND_BASE_URL=http://localhost:1420`.

---

### 2) Dependency setup is still manual and OS-specific

- Backend setup differs between macOS/Linux and Windows.
- Desktop setup requires a separate `npm install`.

**Fix applied:**
- Added `scripts/setup_local.sh` and `scripts/setup_local.ps1` to automate:
  - Python venv creation
  - Backend dependency install
  - `.env` creation + required defaults
  - Desktop dependency install

---

### 3) Optional Playwright browsers are not mentioned in core flow

- `playwright` is listed in backend requirements but browser binaries are not installed by default.
- Scraper workflows will fail unless `python -m playwright install` is run.

**Fix applied:**
- The local setup guide now includes an optional Playwright install note.

---

## ✅ Completed readiness actions

1. **Pinned Node version**
   - Added a repo-level `.nvmrc` to lock Node to 18.x LTS.

2. **Optional Playwright setup**
   - Setup helpers now support `INSTALL_PLAYWRIGHT=1` to install browsers when needed.

3. **Dependency lock support**
   - Added `backend/requirements.lock` with instructions to generate a fully pinned lock file
     using `pip-tools` in a networked environment.

## 📌 Open item

- Generate `backend/requirements.lock` with pinned versions once `pip-tools` can resolve dependencies
  in a networked environment. The setup scripts will automatically prefer the lock file when populated.

---

## ✅ Outcome

With the setup scripts and updated local guide, the repo can now be installed and run more consistently on any PC.
The open lockfile generation item is a quality-of-life improvement rather than a blocker.
