# Local setup guide (Windows/macOS/Linux)

This guide provides a repeatable, cross-platform setup for running GFPS on any development machine.
It focuses on the **FastAPI backend** and the **desktop client** in development mode, plus optional desktop packaging.

---

## ✅ Prerequisites

Install these before running the project:

| Tool | Recommended version | Notes |
| --- | --- | --- |
| **Python** | 3.11+ | Backend and CLI tooling |
| **Node.js** | 18+ (LTS) | Desktop UI (Vite) and Tauri tooling |
| **Git** | Latest | Repository clone and version control |

> If you use `nvm`, run `nvm use` in the repo root to pick up the pinned Node version from `.nvmrc`.

Optional (only for building desktop installers):

| Tool | Recommended version | Notes |
| --- | --- | --- |
| **Rust** | 1.70+ | Required for Tauri builds |
| **Tauri system deps** | OS-specific | WebView/GTK tooling for Linux, Xcode for macOS |

> If you only need the **web UI in dev mode**, Rust/Tauri are not required.

---

## 🧩 1) Clone the repository

```bash
git clone https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System.git
cd G.F.P.S-Global-Football-Probability-System
```

---

## 🤖 Optional: one-command setup helpers

You can run a platform-specific helper that prepares the backend venv, installs dependencies,
and configures `.env` with safe local defaults. If you need the web scraper, add
`INSTALL_PLAYWRIGHT=1` to install Playwright browsers.

### macOS / Linux

```bash
./scripts/setup_local.sh
# With Playwright browsers:
# INSTALL_PLAYWRIGHT=1 ./scripts/setup_local.sh
```

### Windows (PowerShell)

```powershell
.\scripts\setup_local.ps1
# With Playwright browsers:
# $env:INSTALL_PLAYWRIGHT=1; .\scripts\setup_local.ps1
```

---

## 🐍 2) Backend setup (FastAPI)

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

> If `backend/requirements.lock` is populated, you can install pinned versions with
> `pip install -r backend/requirements.lock` instead.

---

## ⚙️ 3) Environment configuration

1. Copy the example env file:

```bash
cp .env.example .env
```

2. Set at least:

```bash
SECRET_KEY=$(openssl rand -hex 32)
```

> On Windows you can use `python -c "import secrets; print(secrets.token_hex(32))"` instead of `openssl`.

3. Update the frontend URL for local password reset links:

```bash
FRONTEND_BASE_URL=http://localhost:1420
```

If you don’t have API keys yet, leave those values blank; the app will use seeded fixtures.

> Optional: If you plan to use the web scraper, install the Playwright browsers with
> `python -m playwright install` after installing backend dependencies.

---

## ▶️ 4) Start the backend

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/health` to confirm the backend is healthy.

---

## 🖥️ 5) Start the desktop UI (dev mode)

In a new terminal:

```bash
cd GFPS/desktop
npm install
npm run dev
```

The UI will connect to `http://localhost:8000` by default.

---

## 📦 6) Build desktop installers (optional)

This step is only required if you want `.msi`, `.dmg`, or `.AppImage` builds.
Ensure **Rust** and **Tauri system dependencies** are installed for your OS first.

```bash
cd GFPS/desktop
npm run tauri:build
```

---

## 🐳 7) Alternative: Docker Compose

```bash
cp .env.example .env
docker compose -f infrastructure/docker-compose.yml up --build
```

---

## 🧪 Optional sanity check

```bash
AUTH_TOKEN="$(curl -s -X POST -H "Content-Type: application/json" -d '{"email":"test@gfps.app","password":"password123"}' http://localhost:8000/auth/signup | jq -r .token)"
AUTH_TOKEN="$AUTH_TOKEN" ./scripts/check_endpoints.sh http://localhost:8000
```

---

## ❗ Troubleshooting tips

- **Port already in use**: change the backend port in your `uvicorn` command, and update the desktop `FRONTEND_BASE_URL` setting.
- **Missing Python packages**: confirm the virtual environment is activated.
- **Node errors**: delete `node_modules` and rerun `npm install`.
- **Tauri build failures**: confirm Rust and the OS-specific WebView dependencies are installed.

---

If you run into a setup issue not covered here, open an issue with your OS version and the exact error output.
