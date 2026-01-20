# Quick Start Guide - GFPS Desktop

This guide helps you get up and running with GFPS Desktop quickly.

## Prerequisites

- **GFPS Desktop App**: Downloaded and installed from [GitHub Releases](https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System/releases)
- **Python 3.8+**: Download from [python.org](https://www.python.org/downloads/)
- **GFPS Repository**: Downloaded or cloned from GitHub

## Step-by-Step Setup

### 1. Install the Desktop App

Choose your platform:

**Windows:**
- Download the `.msi` installer
- Run it and follow the setup wizard
- If you see a SmartScreen warning, click "More info" → "Run anyway"

**macOS:**
- Download the `.dmg` file
- Open it and drag GFPS to Applications
- Right-click the app → "Open" (first time only)

**Linux:**
- Download the `.AppImage` file
- Make executable: `chmod +x GFPS*.AppImage`
- Run: `./GFPS*.AppImage`

### 2. Download the GFPS Repository

You need the repository for the backend server:

**Option A: Download ZIP**
1. Go to https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file to a folder

**Option B: Clone with Git**
```bash
git clone https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System.git
cd G.F.P.S-Global-Football-Probability-System
```

### 3. Start the Backend Server

Navigate to the repository folder and run the startup script:

**Windows:**
```cmd
cd path\to\G.F.P.S-Global-Football-Probability-System
start-backend.bat
```

**macOS/Linux:**
```bash
cd path/to/G.F.P.S-Global-Football-Probability-System
./start-backend.sh
```

The script will:
- ✅ Create a Python virtual environment
- ✅ Install all dependencies
- ✅ Generate a secure SECRET_KEY
- ✅ Initialize the database
- ✅ Start the backend server

Wait for the message:
```
Uvicorn running on http://0.0.0.0:8000
```

### 4. Launch the Desktop App

1. Open GFPS Desktop
2. The app should now connect automatically
3. You'll see the Dashboard with live data

### 5. (Optional) Configure Settings

Go to Settings to:
- Configure data provider API keys (API-Football, Football-Data.org, etc.)
- Create an account or log in
- Adjust refresh intervals and EV thresholds
- Switch themes

## What if the Backend Won't Start?

If the automatic script fails, start manually:

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Create .env file
cp .env.example .env

# 5. Generate SECRET_KEY
# macOS/Linux:
openssl rand -hex 32
# Windows PowerShell:
python -c "import secrets; print(secrets.token_hex(32))"

# 6. Edit .env and set SECRET_KEY=<your-generated-key>

# 7. Start the server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## Common Issues

### "Backend API Not Available"
- Make sure the backend server is running
- Check that http://localhost:8000/health returns `{"ok": true}`
- Verify Settings → API Endpoint is `http://localhost:8000`

### "Port 8000 is already in use"
- Another application is using port 8000
- Start backend on a different port: `uvicorn backend.main:app --port 8001 ...`
- Update Settings → API Endpoint to `http://localhost:8001`

### Backend shows errors about SECRET_KEY
- Edit `.env` file
- Set `SECRET_KEY=` to a 64-character hex string
- Generate one with: `openssl rand -hex 32` or `python -c "import secrets; print(secrets.token_hex(32))"`

### Desktop app won't open on macOS
- Right-click the app in Applications
- Select "Open"
- Click "Open" in the dialog
- This only needs to be done once

## Next Steps

Now that you're set up:

1. **Explore the Dashboard** - See live matches, predictions, and value bets
2. **Configure Data Providers** - Add API keys in Settings for live data
3. **View Value Bets** - Find EV+ opportunities
4. **Track Performance** - Monitor your betting ROI
5. **Run Backtests** - Test strategies on historical data

## Getting Help

- 📖 Full documentation: [docs/](../docs/)
- 🐛 Report issues: [GitHub Issues](https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System/issues)
- 💬 Detailed setup: [README.md](../README.md#-getting-started-locally)

## Security Note

- ⚠️ Never share your SECRET_KEY or API keys
- 🔒 All data stays local on your device
- 🚫 No telemetry or data collection

---

**Enjoy using GFPS! ⚽📊**
