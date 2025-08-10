# GR Rentals — Cloud (Option A)

Hosted, hands-off setup: **GitHub Actions (cron) + Supabase Postgres + Streamlit Cloud**.

## What this repo does
- A scheduled **GitHub Action** runs `scrape_craigslist_pg.py` and writes rows into **Supabase Postgres**.
- A **Streamlit app** (`app.py`) reads from Supabase and shows a public dashboard (optional password).
- No local server. No data or secrets committed.

## One-time setup (about an hour, no local CLI required)

### 0) Create three free accounts
- GitHub
- Supabase
- Streamlit Community Cloud

### 1) Create a new private GitHub repo and upload this folder
- Click **"Add file → Upload files"** and drag/drop the contents of this zip.
- Push/commit.

### 2) Supabase: create project & database
- Create a new Supabase project (free plan is fine).
- Go to **Project Settings → Database → Connection string**.
- Copy the **URI** form (looks like: `postgresql://...:5432/postgres?sslmode=require`). Keep it handy.

### 3) Add GitHub Actions secret
- Repo → **Settings → Secrets and variables → Actions** → **New repository secret**:
  - Name: `DATABASE_URL`
  - Value: (your Supabase Postgres URI)

### 4) Enable the scheduled scraper
- In the repo, open `.github/workflows/scrape.yml` and ensure the cron you want is set (default every 6 hours).
- Actions will run automatically; first run may take a minute.

### 5) Streamlit Cloud deploy
- Go to Streamlit Cloud → **New app** → Connect your GitHub repo.
- Set **Main file path** to `app.py`.
- In **Secrets**, add:
  - `DATABASE_URL = "<Supabase Postgres URI>"`
  - `APP_PASSWORD = "set-a-password-here"` (optional; if empty, no login required)
- Click **Deploy**. You’ll get a public URL to the dashboard.

## Notes
- Table is auto-created on first run if it doesn’t exist.
- Craigslist source uses their **RSS** (TOS-friendly).
- Future sources (Zillow/FB) should be **manual CSV import** or via an approved data provider.
- Modify cron in `.github/workflows/scrape.yml` to change scrape cadence.

## Local dev (optional)
```bash
pip install -r requirements.txt
export DATABASE_URL="postgresql://..."
python scrape_craigslist_pg.py
streamlit run app.py
```
